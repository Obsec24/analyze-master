# Analyze tool

## Configuration

The following files have to be present in the `static/` directory for the tool to work appropiately.


`api.conf`

```
access_key: <ipstack access key>
fields: country_name,location.is_eu
```

`categories`

```
<category 1>: <PII type 1>;<PII type 2>;...
<category 2>: <PII type 3>;<PII type 4>;...
...
```

`info.device`

```
<PII type 1>: <PII 1>;<PII 2>;<PII 3>;...
<PII type 2>: <PII 4>
<PII type 3>: <PII 5>;<PII 6>
...
```

## Usage

To run the tool use the following command:

```
analyze.py <log file> <phase descriptor>
```
Parameters ip_terminal and apk_name are used only for logging purposes
