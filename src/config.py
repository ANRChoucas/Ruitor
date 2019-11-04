data = {
    'MNT': {
        #"path": "/home/mbunel/Données/RGEALTI/RGEALTI_2-0_5M_ASC_LAMB93-IGN69_D038_2017-05-20/",
        #"name": "RGEALTI_38_test.vrt",
        "path": "./data/mnt/",
        "name": "BR.tif"
    }
}

proxy = {
    'url': "http://proxy.ign.fr",
    'port': 3128
}

multiprocessing = {
    'pools': 6
}

log = {
    'int_files': True
}

logging_configuration = {
    'version' : 1,
    'loggers' : {
        'main' : {
            'handlers' : ['console', 'file_debug'],
            'level' : 'DEBUG'
        },
        'spatialisation' : {
            'handlers' : ['console', 'file_debug'],
            'level' : 'DEBUG'
        }
    },
    'handlers' : {
        'console' : {
            'class' : 'logging.StreamHandler',
            'level' : 'INFO'
        },
        'file_debug' : {
            'class' : 'logging.FileHandler',
            'mode' : 'w',
            'filename' : './execution-debug.log',
            'level' : 'DEBUG',
            'formatter' : 'file_formatter'
        }
    },
    'formatters' : {
        'file_formatter' : {
            'format': '%(asctime)s %(levelname)-8s %(name)-15s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    }

}
