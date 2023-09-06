from Sea_Search_Process import Sea_Search_Detection


def main():
    filepath = r'C:\Users\wcamaro\Documents\ECHOES\06Datasets\WP5\Sentinel_Images\Raw_Files\S2B_MSIL2A_20191112T114349_N0213_R123_T29UPU_20191112T142326.zip'

    AOI = {'N': '52.43',
           'E': '-6.23',
           'W': '-6.65',
           'S': '52.23'}

    AdaptiveThresholding_Parameters = {'targetWindowSizeInMeter':'40','guardWindowSizeInMeter':'400.0',        ##### 'targetWindowSizeInMeter':'ONLY ALLOWED INTEGER VALUES'
                                       'backgroundWindowSizeInMeter':'1200.0','pfa':'6.0'
                                       }

    Object_Discrimination_Parameters = {'minTargetSizeInMeter': '40', 'maxTargetSizeInMeter': '400'}


    outputfile = Sea_Search_Detection(filepath, AOI, AdaptiveThresholding_Parameters, Object_Discrimination_Parameters)
    print 'Thanks_Process_Finished %s generated' % outputfile

if __name__ == '__main__':
    main()

