# This script converts the default PrusaSlicer thumbnail header to the format expected by the Ender 3 V2 Neo
# by CrealityExperts - no copyrights, share freely
#
# modified by AMC to convert both the 48x48 and the 200x200 thumbnails
# this is required by at least my version of the Ender 3 Neo V2
#
import re, sys

def fixup_dimensions(dimensions):
    if dimensions == '48x48':
        return '48*48'
    elif dimensions == '200x200':
        return '200*200'
    else:
        return 'dimension_error'

def skip_lines_until_match(linebuf, start_index, pattern):
    for i, line in enumerate(linebuf, start_index):
        if pattern in line:
            return i, line
    return None, None

def correct_thumbnail_jpg_line(line):
    semicolon, thumbnail_string, begin_string, dimensions, length = line.split()
    thumbnail_string = 'jpg'
    begin_string = 'begin'
    dimensions = fixup_dimensions(dimensions)
    length = int(int(length) * 3/4) # data pixel count conversion is required for the Neo V2
    if dimensions == '200*200':
        suffix = '3 197 5001' 
    elif dimensions == '48*48':
        suffix = '1 47 500' 
    else:
        suffix = '? ? ?'
    fixedline = f"; {thumbnail_string} {begin_string} {dimensions} {length} {suffix}\n"
    return fixedline

#the first argument will always be the temporary gcode file prusaslicer generates.  The script applies the updates directly to this temporary file
gcode_filename = sys.argv[1]

# read the entire gcode file into a list of lines
with open(gcode_filename, "r") as f:
    lines = f.readlines()
    f.close()


# collect only the lines we need into outlines
outlines = []

# skip lines until we find the first thumbnail
i, line = skip_lines_until_match(lines, 0, 'thumbnail_JPG')

# correct the syntax and output the fixed up line
fixedline = correct_thumbnail_jpg_line(line)
outlines.append(fixedline)

# output the thumbnail pixel data lines until we reach the thumbnail_JPG end
for j, line in enumerate(lines[i+1:], i+1):
    if "thumbnail_JPG" in line:
        break
    else:
        outlines.append(line)
# add the properly formatted jpd end
outlines.append('; jpg end\n')
outlines.append(';\n')

# skip lines until we find the second thumbnail
k, line = skip_lines_until_match(lines[j+1:], j+1, 'thumbnail_JPG')
# only process the second thumbnail if we found it
if line:
    fixedline = correct_thumbnail_jpg_line(line)
    outlines.append(fixedline)

    # output the data lines until we reach the thumbnail_JPG end
    for m, line in enumerate(lines[k+1:], k+1):
        if "thumbnail_JPG" in line:
            break
        else:
            outlines.append(line)
    # add the properly formatted jpd end
    outlines.append('; jpg end\n')
    outlines.append(';\n')


# The Ender 3 V2 Neo expects these lines to be present before the actual GCode starts
outlines.append(';FLAVOR:Marlin\n')
outlines.append(';TIME:0\n')
outlines.append(';Filament used: 0m\n')
outlines.append(';Layer height: 0\n')
outlines.append(';MINX:1\n')
outlines.append(';MINY:1\n')
outlines.append(';MINZ:1\n')
outlines.append(';MAXX:1\n')
outlines.append(';MAXY:1\n')
outlines.append(';MAXZ:1\n')
outlines.append(';POSTPROCESSED\n')
outlines.append(';\n\n')

# skip lines until we find EXECUTABLE_BLOCK_START
n, line = skip_lines_until_match(lines[m+1:], m+1, 'EXECUTABLE_BLOCK_START')

# copy over all the lines from here on...
outlines.extend(lines[n+1:])

# save the updated file back to the original file location
data = "".join(outlines)
with open(gcode_filename , "w") as of:
    of.write(data)



