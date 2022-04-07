import yaml

app_conf_file = "app_conf.yml"
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
for service in app_config["eventurl"]:
    print(service)
    
