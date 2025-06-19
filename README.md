# Introduction
This script will allow leveraging interval of 6 months to gather all needed info.  
It also gives an option to select the name of one application to show results for that application only.

# Output
The output is in excel.
The output is `veracode_findings.xlsx`.
You decide where the output file is saved to by command line in terminal; see [Launch it](#launch-it)

# Install
`git clone https://github.com/harlockus/veracode-reporting-api-helper.git`

# cd
`cd veracode-reporting-api-helper`

# Install requirements
`pip install -r requirements.txt`

# Authentication

Save Veracode API credentials in `~/.veracode/credentials`

`[default]`

`veracode_api_key_id = <YOUR_API_KEY_ID>`

`veracode_api_key_secret = <YOUR_API_KEY_SECRET>`

# Set your credentials
Set your credentials as envirenment variables with:

`export VERACODE_API_KEY_ID=<YOUR_API_KEY_ID>`

`export VERACODE_API_KEY_SECRET=<YOUR_API_KEY_SECRET>`


# Launch it
How to launch it:

`python3 Reporting_API_1.py \`

`--start-date "YEAR-MM-DD 00:00:00" \`

`--output-dir "the path to where you want the xlsx file to be published"`

Choose the starting date you want.
Write the full path to where you would like the excel file to be saved to.
Follow prompts.

# Note
  Note: Not an official VERACODE product.

# Reporting API documentation
Please visit [VERACODE REPORTING REST API](https://docs.veracode.com/r/Reporting_REST_API) for details.
