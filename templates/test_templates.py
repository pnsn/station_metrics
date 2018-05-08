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
    startdate = UTCDateTime(2018,05,01)
    enddate = UTCDateTime(2018,05,02)
    # define which channel codes denote acceptable seismic channels
    SEISMIC_CHANNELS = ['BHE', 'BHN', 'BHZ', 'HHE', 'HHN', 'HHZ',
                 'BH1', 'BH2', 'BH3', 'HH1', 'HH2', 'HH3',
                 'ENE', 'ENN', 'ENZ', 'HNE', 'HNN', 'HNZ',
                 'EN1', 'EN2', 'EN3', 'HN1', 'HN2', 'HN3']

    for network in inv:
        for station in network:
            with open(station.code + ".html", "w") as fh:
                fh.write(template.render(starttime=startdate,endtime=enddate,network_code=network.code,station=station,allowed=SEISMIC_CHANNELS))
            HTML("./"+station.code+".html").write_pdf(station.code + ".pdf")
            
