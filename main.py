import bpy
from bpy.types import Camera

def read_some_data(context, fileName, use_some_setting):

    print (fileName);

    file = open(fileName, 'r');
    i = 1;
    readVerts = False;
    readCam = False;
    numFrames = 0;

    for curLine in file.readlines():
        # check for correct file header.
        # if it's not found, print an error and exit
        if (i==1) and ('boujou export' not in curLine):
            print ('ERROR: incorrect file header.')
            print ('line #: '+str(i))
            print (' - expecting "# boujou export: text"');
            print (' - found "'+curLine+'"');
            file.close();
            break;
    
    
    ################################################################################
    #
    #  Camera loading code
    #
    ################################################################################
    
        # if we find the string that signifies the end of the file,
        # change our flag to false - we can't read nothing!!
        if (readCam == True):
            coOrds = curLine.split()
            if  (len(coOrds) == 0):
                readCam = False;
                print('('+str(i)+'): Found end of camera block');
                allObj = Object.Get()
                for curObj in allObj:

                    if curObj.name[:10]=='boujou_tmp':
                        cur.unlink(curObj);

    
        # CAMERA FRAME DATA FOUND!!
            else:
                # set the camera rotation/translation matrix
                rX = [float(coOrds[0]), float(coOrds[1]), float(coOrds[2]), 0.0];
                rY = [float(coOrds[3]), float(coOrds[4]), float(coOrds[5]), 0.0];
                rZ = [float(coOrds[6]), float(coOrds[7]), float(coOrds[8]), 0.0];
                tR = [float(coOrds[9]), float(coOrds[10]), float(coOrds[11]), 1.0];
                tmpObj.setMatrix(Mathutils.Matrix(rX, rY, rZ, tR));
                
                # compute the FOV in rad
                fovRad = 2.0*math.atan(float(filmSize[2])/(2.0*float(coOrds[12])));
                # This is working and gives the same fov than doing a 3ds export and reading 
                # directly the fov on that file. 
                
				# This is a dirty workaround ! The theoretical factor here is 16. But I need to put more. Why ?
                # set the lens
                tmpCam.lens = 16.48 / math.tan( fovRad / 2.0);
                
                # add point(keyframe) for camera position IPOs
                locx.addBezier((numFrames+1, tmpObj.LocX))
                locy.addBezier((numFrames+1, tmpObj.LocY))
                locz.addBezier((numFrames+1, tmpObj.LocZ))
    
                # add point(keyframe) for the camera rotation IPOs
                rotx.addBezier((numFrames+1, (tmpObj.RotX*18/3.141593)-18))
                roty.addBezier((numFrames+1, tmpObj.RotY*18/3.141593))
                rotz.addBezier((numFrames+1, tmpObj.RotZ*18/3.141593))

                # add point on IPO curve for lens (focal distance)
                lenscurve.addBezier((numFrames+1, tmpCam.lens))
                                        
                # increment the index used for setting IPOs to point to next frame
                numFrames += 1;
    
		# if '#Filmback Size' is found, then we have the size of the film to compute the FOV
        if ('#Filmback Size ' in curLine):
            filmSize = curLine.split()		
		
        # if '#R(0,0)' is found, then we have the start of the vertex data
        if ('#R(0,0)' in curLine):
            print( '(' +str(i) +'): Camera data found in export file');
            readCam = True;            # set flag to indicate we're in a camera block
            
            cRend = bpy.data.cameras.new("Camera");
            cam_ob = bpy.data.objects.new("Camera", cRend)
            bpy.context.scene.objects.link(cam_ob)
            
            #cRend = bpy.ops.object.camera_add(view_align=True, enter_editmode=False, location=(0, 0, 0), rotation=(1.10871, 0.0132652, 1.14827), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
			
            #cRend = Camera.New('persp');
            cRend.lens = 35.0
            #cRend.setDrawSize(1.0);
            cRend.draw_size = 1.0;
            oRend = bpy.data.objects.new('Camera',None);
            oRend.name = 'BouJou_Cam'
            #oRend.link(cRend);
            
            #cur = Scene.GetCurrent();
            cur = bpy.data.scenes[0];
            #cur.link(oRend);
            bpy.context.scene.camera = oRend
            #cur.setCurrentCamera(oRend);
            ipo = bpy.data.actions.new('render_cam_objipo');
            
            #oRend.setIpo(ipo);
            anim_data = oRend.animation_data_create();
            anim_data.action = ipo;
            
            # create the ipo curves that we'll be needing
            locx = ipo.fcurves.new('LocX');
            locx.interpolation('Linear')
            locy = ipo.addCurve('LocY')
            locy.setInterpolation('Linear')
            locz = ipo.addCurve('LocZ')
            locz.setInterpolation('Linear')
            rotx = ipo.addCurve('RotX')
            rotx.setInterpolation('Linear')
            roty = ipo.addCurve('RotY')
            roty.setInterpolation('Linear')
            rotz = ipo.addCurve('RotZ')
            rotz.setInterpolation('Linear')
            camipo = Blender.Ipo.New('Camera','render_cam_camipo')
            cRend.setIpo(camipo)
            lenscurve = camipo.addCurve('Lens')
            lenscurve.setInterpolation('Linear')
    
            # create the temporary camera that is used to convert our camera matrix
            # into rotation and translation figures. This dummy camera also holds the
            # lens info. This temp camera is needed to create the IPO curves
            tmpCam = Camera.New('persp');
            tmpCam.lens = 35.0;
            tmpObj = Object.New('Camera');
            tmpObj.name = 'boujou_tmp'
            tmpObj.link(tmpCam);
            cur.link(tmpObj);



        ################################################################################
        #
        #  Vertex loading code
        #
        ################################################################################
        # if we find the string that signifies the end of the file,
        # change our flag to false - there's nothing left to read
        if ('#End of boujou export file' in curLine):
            print( '(' +str(i) +'): Found end of boujou export file');
            readVerts = False;
            mesh.update()
            cur.update()

        # if we're currently allowed to read vertex positions, then
        # split the line up into individual 'words' - putting the first 3
        # into a 3 element array used to hold 1 point
        if (readVerts==True):
            coOrds = curLine.split();
            if len(coOrds):
                x = float(coOrds[0]);
                y = float(coOrds[1]);
                z = float(coOrds[2]);
                v = NMesh.Vert(x, y, z)
                mesh.verts.append(v);
    
        # if '#x y z' is found, then we have the start of the vertex data
        # (the x, y and x are all separated with tab characters (\t))
        if ('#x\ty\tz' in curLine):
            readVerts = True;

            ob = Object.New('Mesh', 'BouJouData')
            ob.setLocation(0.0, 0.0, 0.0)
            mesh = ob.getData();
            cur = Scene.getCurrent()
            cur.link(ob)

            print( '(' +str(i) +'): Vertex data found in export file');
        ##########################################################################

        # increment the file's line counter
        i += 1;
        ########### End of loop performed on each lie of the file ################
        
    print ('Total of '+str(numFrames)+' frames tracked.');
    file.close();

    return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportSomeData(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Some Data"

    # ImportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob = StringProperty(
            default="*.txt",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting = BoolProperty(
            name="Example Boolean",
            description="Example Tooltip",
            default=True,
            )

    type = EnumProperty(
            name="Example Enum",
            description="Choose between two items",
            items=(('OPT_A', "First Option", "Description one"),
                   ('OPT_B', "Second Option", "Description two")),
            default='OPT_A',
            )

    def execute(self, context):
        return read_some_data(context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text="Text Import Operator")


def register():
    bpy.utils.register_class(ImportSomeData)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportSomeData)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_test.some_data('INVOKE_DEFAULT')