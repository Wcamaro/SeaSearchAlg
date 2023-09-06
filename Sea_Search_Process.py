import os
import subprocess
from zipfile import ZipFile


def write_XML_parameters(dict):
  xml_parameters = '\t<parameters class="com.bc.ceres.binding.dom.XppDomElement">\n'
  dict.keys().sort()
  for parameter in dict.keys():
    if dict[parameter] == '':
      xml_parameters = xml_parameters + '\t <%s/>\n' % parameter
    else:
      xml_parameters = xml_parameters + '\t <%s>%s</%s>\n' % (parameter,dict[parameter],parameter)
  xml_parameters = xml_parameters + '\t </parameters>\n'
  return xml_parameters

def write_XML_sources(source):
    if source == '':
        xml_sources =  '\t <sources/>\n'
    else:
        xml_sources = '<sources>\n\t <sourceProduct refid="%s"/>\n\t</sources>\n' % source
    return xml_sources



def Write_XML_FILE(filename, AOI,xmlfile,Ad_Th_Par,Obj_Det_Par):
  outpath = '\\'.join(filename.split('\\')[:-3])+'\\'+'Objected_Detected_Output'+'\\'
  if not os.path.exists(outpath):
      os.makedirs(outpath)
  outputfile = outpath+(filename.split('\\')[-2][:-5])+'_Cal_THR_SHP'


  Sources_GrapXML = {   'Read':'',
                        'Ellipsoid-Correction-GG':'Read',
                        'Subset':'Ellipsoid-Correction-GG',
                        'Land-Sea-Mask': 'Subset',
                        'Calibration':'Land-Sea-Mask',
                        'Speckle-Filter':'Calibration',
                        'AdaptiveThresholding':'Speckle-Filter',
                        'Object-Discrimination':'AdaptiveThresholding',
                        'Write':'Object-Discrimination'}


  Parameters_GrapXML = {'Read':({'file':filename,'formatName':'SENTINEL-1'}),
                        'Ellipsoid-Correction-GG':({'sourceBands':'','imgResamplingMethod':'BILINEAR_INTERPOLATION',
                                                    'mapProjection':'EPSG:3857'}),
                        'Subset':({'sourceBands':'','region':'','geoRegion':AOI,'subSamplingX':'1',
                                   'subSamplingY':'1','fullSwath':'false','tiePointGridNames':'','copyMetadata':'true'}),
                        'Land-Sea-Mask':({'sourceBands':'','landMask':'true','useSRTM':'true','geometry':'',
                                          'invertGeometry':'false','byPass':'false'}),
                        'Calibration':({'sourceBands':'','auxFile':'Product Auxiliary File','externalAuxFile':'',
                                        'outputImageInComplex':'false','outputImageScaleInDb':'false',
                                       'createGammaBand':'false','createBetaBand':'false','selectedPolarisations':'',
                                        'outputSigmaBand':'True','outputBetaBand':'false','outputGammaBand':'false'}),
                        'Speckle-Filter':({'sourceBands':'','filter':'Gamma Map','filterSizeX':'3','filterSizeY':'3',
                                           'dampingFactor':'2','estimateENL':'true','enl':'1.0','numLooksStr':'1',
                                           'windowSize':'7x7','targetWindowSizeStr':'3x3','sigmaStr':'0.9','anSize':'50'}),
                        'AdaptiveThresholding':({'targetWindowSizeInMeter':Ad_Th_Par['targetWindowSizeInMeter'],
                                                 'guardWindowSizeInMeter':Ad_Th_Par['guardWindowSizeInMeter'],
                                                 'backgroundWindowSizeInMeter':Ad_Th_Par['backgroundWindowSizeInMeter'],
                                                 'pfa':Ad_Th_Par['pfa'],'estimateBackground':'false'}),
                        'Object-Discrimination':({'minTargetSizeInMeter':Obj_Det_Par['minTargetSizeInMeter'],
                                                  'maxTargetSizeInMeter':Obj_Det_Par['maxTargetSizeInMeter']}),
                        'Write':({'file':outputfile,'formatName':'GeoTIFF'})}

  xmlGraph = '<graph id="Graph">\n\t<version>1.0</version>\n'
  xmlAppData = '\t<applicationData\tid="Presentation">\n\t <Description/>\n'


  for node in Sources_GrapXML.keys():
    xmlGraph = xmlGraph + '\t<node\tid="%s">\n\t<operator>%s</operator>\n' % (node,node)
    xmlSourc = write_XML_sources(Sources_GrapXML[node])
    xmlPar=write_XML_parameters(Parameters_GrapXML[node])
    xmlGraph = xmlGraph + xmlSourc + xmlPar
    xmlGraph = xmlGraph + '\t</node>\n'
    xmlAppData = xmlAppData + '\t <node\tid="%s">\n\t  <displayPosition x="0.0" y="0.0"/>\n\t </node>\n' % node

  xmlAppData = xmlAppData + '\t</applicationData>\n'
  xmlGraph = xmlGraph +xmlAppData + '</graph>\n'




  file = open(xmlfile, 'w')
  file.write(xmlGraph)
  file.close()
  return outputfile



def do_unzip_sentinel(input_path, outpath):
    filepath=ZipFile(input_path)
    ZipFile.extractall(filepath, outpath)

def AOI_TO_Geom(N, W, E, S):
    geom = "POLYGON ((%s %s, %s %s, %s %s, %s %s, %s %s))"  % (W,N,E,N,E,S,W,S,W,N)
    return geom

def Sea_Search_Detection(filepath,AOI,Ad_Th_Par,Obj_Det_Par):

    raw_sentinel_path = '\\'.join(filepath.split('\\')[:-2])+'\\RAW_SENTINEL'
    if not os.path.exists(raw_sentinel_path):
        os.makedirs(raw_sentinel_path)
    do_unzip_sentinel(filepath, raw_sentinel_path)
    file_Sentinel = raw_sentinel_path + '\\'+ filepath.split('\\')[-1][:-4] + '.SAFE'
    print 'Extracting %s in \t %s' % (filepath, file_Sentinel)
    file_input = file_Sentinel+'\\'+'manifest.safe'

    polygon = AOI_TO_Geom(AOI['N'],AOI['W'],AOI['E'],AOI['S'])
    xml_file = raw_sentinel_path + '\\' + 'GFP_xml.xml'
    outputfile = Write_XML_FILE(file_input,polygon,xml_file,Ad_Th_Par,Obj_Det_Par)
    gpt_Command = "gpt %s " % xml_file
    print ('\n invoking: ' + gpt_Command)
    try:
        process = subprocess.Popen(gpt_Command,
                                   shell=True,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, )
        # Reads the output and waits for the process to exit before returning
        stdout, stderr = process.communicate()
        print (stdout)
        if stderr:
            raise Exception(stderr)  # or  if process.returncode:
        if 'Error' in stdout:
            raise Exception()
    except Exception, message:
            print(str(message))
            

    return outputfile