import hou

# Ask the user for the files
# Geometry node
# File node for FBX and OBJ, BGEO
# If is Alembic we use an Alembic Loader
# Transform and set the scale to 0.01
# Add Material node
# Merge Node
# add ALERT MESSAGE

# 1. Declaring Variables and opening the File Chooser
default_directory = hou.text.expandString('$HIP')
select_directory = hou.ui.selectFile(
    start_directory=default_directory,
    title="Select the files you want to import",
    file_type=hou.fileType.Geometry, 
    multiple_select=True
)

# 2. Check if the user actually selected a file
if select_directory:
    # multiple_select returns a string separated by semicolons; split them into a list
    select_directory = select_directory.split(';')

    # Create the main container and merge node
    obj = hou.node('/obj')
    geo_node = obj.createNode('geo', node_name='tempGeo')
    merge_node = geo_node.createNode('merge', node_name='MergeAll')
    
    # Initialize connection index for the merge node
    add_to_merge = 0

    for item in select_directory:
        item = item.strip()
        
        # Split the path to get the filename, then split the filename to get the extension
        asset = item.split('/')
        filename_with_ext = asset[-1]
        
        # Safe extraction of name and extension
        object_parts = filename_with_ext.split('.')
        node_name = object_parts[0]
        extension = object_parts[-1].lower() 

        # 3. Alembic (.abc) specific workflow
        if extension == 'abc':
            new_alembic_loader = geo_node.createNode('alembic', node_name=node_name)
            new_alembic_loader.parm('fileName').set(item)

            unpack_node = geo_node.createNode('unpack', node_name=node_name + '_unpack')
            unpack_node.setInput(0, new_alembic_loader)

            transform_node = geo_node.createNode('xform', node_name=node_name + '_xform')
            transform_node.parm('scale').set(0.01)
            transform_node.setInput(0, unpack_node)

            material_node = geo_node.createNode('material', node_name=node_name + '_mat')
            material_node.setInput(0, transform_node)
            
            # Connect the final material node into the Merge node
            merge_node.setInput(add_to_merge, material_node)

        # 4. Standard Geometry (OBJ, FBX, etc.) workflow
        else:
            new_file_loader = geo_node.createNode('file', node_name=node_name)
            new_file_loader.parm('file').set(item)

            transform_node = geo_node.createNode('xform', node_name=node_name + '_xform')
            transform_node.parm('scale').set(0.01)
            transform_node.setInput(0, new_file_loader)
            
            # Connect the final transform node into the Merge node
            merge_node.setInput(add_to_merge, transform_node)

        # Increment the merge input index for the next loop iteration
        add_to_merge += 1

    # Automatically layout the nodes cleanly so they aren't stacked
    geo_node.layoutChildren()

# 5. NEW: UI Message if no file is selected
else:
    hou.ui.displayMessage("Please, check again. No valid file was selected", buttons=('OK',))
    

