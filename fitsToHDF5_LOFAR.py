from astropy.io import fits
import h5py
import numpy as np
import sys

if len(sys.argv) < 2:
    print("Usage: {} <input file> <Stokes parameter to assign (opt)>".format(sys.argv[0]))
    quit(1)

inputFileName = sys.argv[1]
stokesParm = ''
if len(sys.argv) < 3:
    print('No Stokes parameter specified')
else:
    stokesParm = sys.argv[2][0]
    print('Using Stokes parameter {}'.format(stokesParm))

try:
    with fits.open(inputFileName) as inputFits:
        dims = inputFits[0].data.shape
        if len(dims) == 3:
            print('3D FITS file found, converting to HDF5 using LOFAR-USG-ICD-004 data structure')
            outputFileName = inputFileName + ".hdf5"
            outputFileName = outputFileName.replace(".fits", "")
            outputFileName = outputFileName.replace(".FITS", "")
            header = inputFits[0].header  # type: fits.Header

            try:
                with h5py.File(outputFileName, "w") as outputHDF5:
                    syslogGroup = outputHDF5.create_group("SysLog")
                    if header['HISTORY']:
                        historyVals = []
                        for val in header['HISTORY']:
                            historyVals.append(np.string_(val))
                        syslogGroup.attrs.create('HISTORY', historyVals)

                    if header['COMMENT']:
                        commentVals = []
                        for val in header['COMMENT']:
                            commentVals.append(np.string_(val))
                        syslogGroup.attrs.create('COMMENT', commentVals)

                    imageGroupExpression = 'Image{0:03d}'
                    if dims[0] > 999:
                        imageGroupExpression = 'Image{0:04d}'
                    for subBand in range(dims[0]):
                        sliceShape = dims[1:]
                        sliceData = inputFits[0].data[subBand, :, :]
                        currentGroup = outputHDF5.create_group(imageGroupExpression.format(subBand))
                        coordinatesGroup = currentGroup.create_group("Coordinates")
                        directionCoordinatesGroup = coordinatesGroup.create_group("DirectionCoordinates")
                        if header['CTYPE1']:
                            directionCoordinatesGroup.attrs.create('CTYPE1', np.string_(header['CTYPE1']))
                        if header['CRVAL1']:
                            directionCoordinatesGroup.attrs.create('CRVAL1', float(header['CRVAL1']))
                        if header['CRPIX1']:
                            directionCoordinatesGroup.attrs.create('CRPIX1', float(header['CRPIX1']))
                        if header['CDELT1']:
                            directionCoordinatesGroup.attrs.create('CDELT1', float(header['CDELT1']))
                        if header['CROTA1']:
                            directionCoordinatesGroup.attrs.create('CROTA1', float(header['CROTA1']))

                        if header['CTYPE2']:
                            directionCoordinatesGroup.attrs.create('CTYPE2', np.string_(header['CTYPE2']))
                        if header['CRVAL2']:
                            directionCoordinatesGroup.attrs.create('CRVAL2', float(header['CRVAL2']))
                        if header['CRPIX2']:
                            directionCoordinatesGroup.attrs.create('CRPIX2', float(header['CRPIX2']))
                        if header['CDELT2']:
                            directionCoordinatesGroup.attrs.create('CDELT2', float(header['CDELT2']))
                        if header['CROTA2']:
                            directionCoordinatesGroup.attrs.create('CROTA2', float(header['CROTA2']))

                        if header['EQUINOX']:
                            directionCoordinatesGroup.attrs.create('EQUINOX', float(header['EQUINOX']))

                        spectralCoordinatesGroup = coordinatesGroup.create_group("SpectralCoordinate")
                        if header['CTYPE3']:
                            spectralCoordinatesGroup.attrs.create('CTYPE3', np.string_(header['CTYPE3']))
                        if header['CRVAL3']:
                            spectralCoordinatesGroup.attrs.create('CRVAL3', float(header['CRVAL3']))
                        if header['CRPIX3']:
                            spectralCoordinatesGroup.attrs.create('CRPIX3', float(header['CRPIX3']))
                        if header['CDELT3']:
                            spectralCoordinatesGroup.attrs.create('CDELT3', float(header['CDELT3']))
                        if header['CROTA3']:
                            spectralCoordinatesGroup.attrs.create('CROTA3', float(header['CROTA3']))

                        polarizationCoordinateGroup = coordinatesGroup.create_group("PolarizationCoordinate")
                        polarizationCoordinateGroup.attrs.create('MultiStokes', False)
                        if len(stokesParm):
                            polarizationCoordinateGroup.attrs.create('StokesCoordinates', np.string_(stokesParm))

                        sourceTableGroup = currentGroup.create_group("SourceTable")
                        if header['TELE']:
                            sourceTableGroup.attrs.create('TELE', np.string_(header['TELE']))
                        if header['OBSERVER']:
                            sourceTableGroup.attrs.create('OBSERVER', np.string_(header['OBSERVER']))
                        if header['INSTR']:
                            sourceTableGroup.attrs.create('INSTR', np.string_(header['INSTR']))

                        processingHistoryGroup = currentGroup.create_group("ProcessingHistory")
                        dataSet = currentGroup.create_dataset("Data", sliceShape, dtype='f4', data=sliceData)
                        if header['BUNIT']:
                            dataSet.attrs.create('BUNIT', np.string_(header['BUNIT']))
                        if len(stokesParm):
                            dataSet.attrs.create('Stokes', np.string_(stokesParm))

                        print("Finished processing {}".format(currentGroup.name))

            except OSError as error:
                print("Unable to create file {}".format(outputFileName))
                print(error)
        else:
            print('Only 3D FITS files supported for now')
            quit(1)

except FileNotFoundError as error:
    print("File {} not found!".format(inputFileName))
    print(error)
    quit(1)