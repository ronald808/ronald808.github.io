---
layout: post
title: Code generation and data format parsing
--- 

Writing binary data parsers is not overly exciting. Unfortunately, in a field where each sensor system has its own binary format, we have accumulated a lot of code dealing with parsing remote sensing data raw files.

With a bit of experience, a few common features emerge: 

- Most formats (but not all) are packet-based since the majority of sensors transmit data through UDP or TCP. 
- Meta-Data is stored in fixed-size fields 
- Data consist of 1D or 2D array of fixed-size samples. Array size can be inferred from preceding packets (headers)
- Multiple meta-data packets may shared the same time base ( i.e. same time-stamps since they are sampled at the same time)

Now, what parsing output do we need?. 

**For Meta-Data** we need to standardize the fields: e.g: "longitude" is always in *decimal* degrees, "depth" is *positive* meters, etc. so that unit and conventions are implicit and not stored. GUI code will convert values to user-selected display units.  

**For Data**, we standardize data representation as well: all 2D imagery shares the same structure for instance. 

There are extra bits of information we need to carry around too. For example if we have extracted the following records:

{% highlight  cpp %}
struct NavFromFormatA {
	double 	timestamp;
	double	longitude;
	double  latitude;
	float 	trueHeading;
};

struct NavFromFormatB {
	double 	timestamp;
	float	roll;
	float	pitch;
	float 	magneticHeading;
	double	longitude;
	double  latitude;
};
{% endhighlight %}

It would be nice to have a "meta" information on the structure so to know the *type* of each field ( e.g. time, longitude, latitude, etc.), a description of the field ( "longitude from Packet XYZ in format B" )
The simple API to query these meta-info may look like this:

{% highlight  cpp %}
// struture meta API:
const char*     packetName();
int             fieldCount();
UID_t           packetUID();
// field meta API:
const char*     fieldName( int i );
const char*     fielDescription( int i );
int             fieldOffset( int i );
FieldEncoding   fieldEncoding( int i );
MetaType        fieldType( int i );
{% endhighlight %}										 

Of course we should implement these function as static class member accessing only static data as we do not want to store any meta-info per class instance. 

Now, we will have a LOT of different packet types, so we describe packets in a XML file and generate our C++ code with a python script: 

![graph](/assets/images/graph1.png)

 
For example, <code>NavFromFormatA.xml</code> could look like this:
{% highlight  xml %}
    <packetdef>
	    <name>NavFromPacketA</name>
	    <field>
	      <id>Time</id>
	      <type>Meta_TimeAbs</type>
	      <encoding>f64</encoding>
	      <desc>Nav Header TimeStamp</desc>
	    </field>
	    <field>
	      <id>Longitude</id>
	      <type>Meta_WGS84Lon</type>
	      <encoding>f64</encoding>
	      <desc>Nav Header Longitude</desc>
	    </field>
	    <field>
	      <id>Latitude</id>
	      <type>Meta_WGS84Lat</type>
	      <encoding>f64</encoding>
	      <desc>Nav Header Latitude</desc>
	    </field>
	    <field>
	      <id>Heading</id>
	      <type>Meta_TrueHeading</type>
	      <encoding>f32</encoding>
	      <desc>Nav Header True Heading</desc>
	    </field>
	</packetdef>
{% endhighlight %}

We usually group all packets for a given format into a single .xml file and integrate code-generation to our build process. 

Binary parser code will convert proprietary binary streams into instances of the generated packets which can be consumed by the application(event-driven) or logged (binary log, convert to SQL, etc.)

The nice thing about this approach is that we only pay for what we need: There's not memory overhead (Plain-Old-Type equivalent) so casting is easy when converting to/from binary streams. We still have the safety provided by the type system (compare to binary blobs) and we support basic "introspection" to facilitate data presentation, data query, storage, reporting, etc. on the application side.

###Parsing the Binary Streams###
For many proprietary binary format we may go a step further and automate binary  parsing a bit. Let's define a "token" base class:

{% highlight  cpp %}
	class Token {
	  public:
		virtual ~Token(){}
		//! @returns the ACTUAL number of bytes read. (-1 -> error)
		virtual __int64		readToken( Stream* src, int nBytes ) 
		virtual int			nBytes() const			 =0;
	};
{% endhighlight %}

and template derived class to wrap our "generated" classed:

{% highlight  cpp %}
template< class Struct_t > 
class TokenTpl : public Token {
  public:
	TokenTpl() {}
	// --- Token: ---
	virtual int		readToken( Stream* src_p, int n )	{ _ASSERT( n == sizeof( d_val ) ); return src_p->read( reinterpret_cast< char*>(&d_val), sizeof( d_val ) ); }
	virtual int			nBytes() const						{ return sizeof( d_val ); }	
  private:
	Struct_t d_val;
};
{% endhighlight %}
and another one for the arrays :
{% highlight  cpp %}
template< class Arr_t > 
class TokenArr : public Token {
  public:
	TokenArr() {}
	// --- Token: ---
	virtual int		readToken( Stream* src_p, int nBytes )	{
								_ASSERT( nBytes % sizeof( d_val[0] ) == 0 );
								d_val.resize( nBytes / sizeof( d_val[0] ) );
								return nBytes ==0 ? 0  : src_p->read( reinterpret_cast< char*>(d_val.data() ), nBytes ); 
								};
	virtual int			nBytes() const						{ return d_val.size() * sizeof( d_val[0] ); } 
  private:
	Arr_t d_val;
};
{% endhighlight  %}


We can now declare our parser:

{% highlight  cpp %}
class ParserBase { 
  public:
	virtual ~TokenParserBase() {}
	virtual int		parse_some( Stream* in_p ) {...} // 
	virtual void	resetParser();
 protected:
	void			addNode(  Token& tok );
	typedef boost::function< int () > SizeFct;
	void			addNode( Token& tok, SizeFct sizeFct );

	virtual void	_interpretChain() =0; 

class MyParser : public ParserBase {
  public:	
	MyParser() {
		// construct the token chain
		addNode( d_nav );
		addNode( d_info );
		//use lambda function to return the size of the data (using a field in the SensorInfoPacket) 
		addNode( d_data, [this]()->int{ return this->d_info.nSamples() * sizeof( short ); } );
	}
  protected:
	virtual void	_interpretChain() 	{...} 
  private:
	// the token sequence:
	mdl::TokenTpl< NavPacket >						d_nav;
	mdl::TokenTpl< SensorInfoPacket >				d_info;
	mdl::TokenArr< std::vector< unsigned short > >	d_data;
};
{% endhighlight  %}
The parser defines the token chain in its constructor and the base class will handle reading the token one at a time and then call <code>MyParser::_interpretChain()</code>. The actual size of <code>d_data</code> to be read depends on a field in <code>d_info</code> so we use a lambda function to return this value for each chain.

The ParserBase class define the logic for error handling, progress notification and waiting on data to read full tokens (i.e. TCP Stream) so that each parser implementation doesn't have to duplicate this logic and can focus on format specific processing.    