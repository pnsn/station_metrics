def configure(filename=None):
    """
        Creates dictionary to pass to a sqlalchemy.engine_from_config() call
    """
    import os

    configuration = {}
    if filename:
        # file the configuration dictionary using parameters from file
        try:
            with open(filename) as fp:
                for line in fp:
                    if line[0] != "#":
                        k,v = line.split("=")
                        configuration[k.strip()] = v.strip()
        except:
            raise
    else:
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_NAME = os.getenv("DB_NAME", "station_metrics")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_USER = os.getenv("DB_USER", "seis")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        if not DB_PASSWORD:
            DB_PASSWORD = raw_input("Password for user {} on {}: ".format(DB_USER,DB_NAME))
        configuration["sqlalchemy.url"] = "postgresql://{}:{}@{}:{}/{}".format(DB_USER,DB_PASSWORD,DB_HOST,DB_PORT,DB_NAME)
    return configuration
