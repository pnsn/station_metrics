from jinja2 import Environment, FileSystemLoader, select_autoescape
from obspy import read_inventory, UTCDateTime
from weasyprint import HTML

if __name__ == "__main__":
    env = Environment(
        loader=FileSystemLoader("./"),
        autoescape=select_autoescape(['html', 'htm', 'xml'])
    )
    template = env.get_template('phase1.htm')
    # get some data to render
    inv = read_inventory("inventory.xml")
    startdate = UTCDateTime(2018,5,1)
    enddate = UTCDateTime(2018,5,2)
    # define which channel codes denote acceptable seismic channels
    SEISMIC_CHANNELS = ['BHE', 'BHN', 'BHZ', 'HHE', 'HHN', 'HHZ',
                 'BH1', 'BH2', 'BH3', 'HH1', 'HH2', 'HH3',
                 'ENE', 'ENN', 'ENZ', 'HNE', 'HNN', 'HNZ',
                 'EN1', 'EN2', 'EN3', 'HN1', 'HN2', 'HN3']

    for network in inv:
        for station in network:
            channel_metrics = {}
            for chan in station:
                 if chan.code in SEISMIC_CHANNELS:
                     if chan.location_code == "":
                         loc = "--"
                     else:
                         loc = chan.location_code
                     nslc = ".".join([network.code,station.code,chan.code,loc])
                     metrics = { 
                                "spikes_total": (0.2*24, "no_threshold"), \
                                "spikes_per_hour": (0.2, "pass"), \
                                "rms_exceeded_per_hour": (2.1, "pass"), \
                                "clock_lock_lcq" : (50, "fail"), \
                                "clock_phase_lce" : (5040/1.0E6, "fail"),  \
                                "acceptable_latency" : (97.3, "fail")
                               }
                     if nslc not in channel_metrics:
                         channel_metrics[nslc] = metrics

            with open(station.code + ".html", "w") as fh:
                fh.write(template.render(starttime=startdate,endtime=enddate, \
                         network_code=network.code,station=station,allowed=SEISMIC_CHANNELS, \
                         metrics=channel_metrics))
            HTML("./"+station.code+".html").write_pdf(station.code + ".pdf")
