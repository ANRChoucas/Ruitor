data = {
    "MNT": [
        {
            "name": "default",
            "precision": 5,
            "path": "/home/mbunel/Données/RGEALTI/RGEALTI_2-0_5M_ASC_LAMB93-IGN69_D038_2017-05-20/",
            "filename": "RGEALTI_38_test.vrt",
        },
        {"name": "HR", "precision": 10, "path": "./data/mnt/", "filename": "HR.tif"},
        {
            "name": "HR_Veymont",
            "precision": 5,
            "path": "./data/mnt/",
            "filename": "HR_Veymont.tif",
        },
        {"name": "MR", "precision": 25, "path": "./data/mnt/", "filename": "MR.tif"},
        {"name": "BR", "precision": 50, "path": "./data/mnt/", "filename": "BR.tif"},
    ]
}

ontology = [
    {
        "type": "SRO",
        "path": "./data/ontologies/",
        "filename": "relations_spatiales.owl",
    },
    {"type": "ROO", "path": "./data/ontologies/", "filename": "todo",},
]

proxy = {"url": "http://proxy.ign.fr", "port": 3128}

multiprocessing = {"pools": 6}

log = {"int_files": True}

logging_configuration = {
    "version": 1,
    "loggers": {
        "__main__": {"handlers": ["console", "file_debug"], "level": "DEBUG"},
        "spatialisation": {"handlers": ["console", "file_debug"], "level": "DEBUG"},
        "ontologyTools": {"handlers": ["console", "file_debug"], "level": "DEBUG"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "level": "INFO"},
        "file_debug": {
            "class": "logging.FileHandler",
            "mode": "w",
            "filename": "./execution-debug.log",
            "level": "DEBUG",
            "formatter": "file_formatter",
        },
    },
    "formatters": {
        "file_formatter": {
            "format": "%(asctime)s %(levelname)-8s %(name)-10s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
}
