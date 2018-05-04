from jinja2 import Environment, FileSystemLoader, select_autoescape

if __name__ == "__main__":
    env = Environment(
        loader=FileSystemLoader("./"),
        autoescape=select_autoescape(['html', 'htm', 'xml'])
    )
    channel = {'net' : 'UW', 'sta' : 'LUMI'} 
    template = env.get_template('phase1.htm')
    print template.render(channel=channel)
