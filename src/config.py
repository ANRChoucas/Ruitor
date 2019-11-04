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
            'handlers' : ['console'],
            'level' : 'DEBUG'
        },
        'spatialisation' : {
            'handlers' : ['console'],
            'level' : 'INFO'
        }
    },
    'handlers' : {
        'console' : {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG'
        }
    }

}
