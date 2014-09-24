from PythonMagick import *

#reading image:

def sliceAll() :
	data=[
		file('raz1.png','rb').read(),
		file('raz2.png','rb').read(),
		file('raz3.png','rb').read()
		]
	loop = 0;
	for ablob in data :
		for y in range( 0,3 ) :
			for x in range(0,3):
				img=Image(Blob(ablob))
				img.crop( Geometry(256,256, 256*x,256*y ) )
				img.write( "slice%d.%d.%d.png" %(loop,x,y))
		loop = loop+1;


def rearrange( coord, fnout ) :
	#create the texture buffer:
	img = Image( Geometry( 4*256, 3*256,0,0), "#999999ff" );
	#img.read( "raz1.png")

	loop =0;
	for cd  in coord :
		img2 = Image()
		img2.read( "slice%d.%d.%d.png" % cd )
		x = loop % 4;
		y = loop / 3;
		img.composite( img2, 256*x, 256*y, CompositeOperator.OverCompositeOp )
		loop = loop +1;
	print( "writing %s" % fnout );
	img.write( fnout)


def drawGrid( fn, fnout ):
	img = Image();
	img.read( fn );
	w = img.columns();
	h = img.rows();
	for x in range (0, w+1, 256 ) :
		if x == w :
			x = w-1
		img.draw( DrawableLine(x, 0, x, h ) )
	for y in range (0, h+1, 256 ) :
		if y == h :
			y = h-1
		img.draw( DrawableLine(0, y, w, y ) )
	print( "writing %s" % fnout );
	img.write( fnout)

	# coord = [
	# 	# (0,0),
	# 	# (1,0),
	# 	(0, 2,0),
	# 	(0, 0,1),
	# 	(0, 2,2),
	# 	(0, 1,1),
	# 	(0, 0,2),
	# 	(0, 2,1),
	# 	(0, 1,2)
	# ]
	
	#rearrange( coord, "tilecache-before.png" );
	#drawGrid( "tilecache.png", "tilecache-grid.png");
	#drawGrid( "raz1.png", "raz1-grid.png");
	#drawGrid( "raz3.png", "raz3-grid.png");

coord2 = [
	 	# (0,0),
	 	# (1,0),
	 	(2, 2,0),
	 	(2, 0,1),
	 	(2, 2,2),
	 	(2, 1,1),
	 	(2, 0,2),
	 	(2, 2,1),
	 	(2, 1,2),
	 	(2, 1,0)
	 ]
rearrange( coord2, "tilecache-after.png");
drawGrid( "tilecache-after.png", "tilecache-after-grid.png");