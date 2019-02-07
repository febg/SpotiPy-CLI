import click
import os
from spotify import auth #felipe did not know this line, bruno wrote this :)
import json
import time

check = u'\u2713' 


@click.group()
@click.pass_context
def main(ctx):
	"""
	An experiment to be able to control spotify without leaving your terminal\n
	WIP:\n
		-> Persist User login, store tokens in a different/same file?
	"""
	ctx.obj = auth.ClientCredential()

	pass

@main.command()
@click.pass_context
@click.argument('client-key', envvar="CLIENT_KEY", required=False)
@click.argument('client-secret', envvar="CLIENT_SECRET", required=False)
@click.option('--config-file', type=click.Path(), required=False)
def config(ctx, client_key, client_secret, config_file):
	"""
	Set and store spotify user credentials \n
	[ Option 1 ]: \n 
	Run the config command with no options and input credentials when prompt\n
	[ Option 2 ]: \n 
	Use the -k and -s flags to pass your credentials as options\n
	[ Option 3 ]: \n
	Set your credentials as ENV varibales "CLIENT_KEY" and "CLIENT_SECRET"\n
	[ Option 4 ]: \n
	Use the -c flag to pass a json config file with "client_key" and "client_secret" fields\n
	"""
	click.echo('[ INFO ] Setting up your credentials..')
	# Ask user to input credentials, or validate from env variables
	if not config_file:
		client_key = click.prompt(
			"Please enter your CLIENT_KEY",
			default=client_key
		)
		client_key = click.prompt(
			"Please enter your CLIENT_SECRET",
			default=client_secret
		)

	if config_file:
		file_name = os.path.expanduser(config_file)

	cli_secrets = os.path.expanduser('./spotify/credentials/credentials.json')
	
	# Load credentials from json config file
	if config_file:
		with open(file_name) as json_file:
			json_data = json.load(json_file)
			if not json_data['client_key']:
				raise click.BadOptionUsage('client_key','Missing client_key credential, please check your config file')
			if not json_data['client_secret']:
				raise click.BadOptionUsage('client_secret','Missing client_secret credential, please check your config file')
	else:
		json_data = {
			'client_key': client_key,
			'client_secret': client_secret
		}
	ctx.obj.set_client_credentials(json_data['client_key'], json_data['client_secret'])
	# Store credentials inside CLI filesystem for re-use
	with open(cli_secrets, 'w') as cli_secrets_file:
			json.dump(json_data, cli_secrets_file)
			#TODO: create a log library to handle info, success, error
			click.echo(click.style('[ '+check+' ] Credentials setup completed..', fg='green'))
			return


	
@main.command()
@click.pass_context
def login(ctx):

	click.echo('[ INFO ] Authenticating credentials with spotify servers..')
	# Check for credentials filesystem
	client_key, client_secret = load_credentials()
	try:
		ctx.obj.set_client_credentials(client_key, client_secret)
	except Exception as error:
		return click.ClickException(error)
	#TODO: create a log library to handle info, success, error
	click.echo(click.style('[ '+check+' ] Authentication successful..', fg='green'))
	#print('After try', code, response)

def load_credentials():
	cli_secrets = os.path.expanduser('./spotify/credentials/credentials.json')
	if not os.path.isfile(cli_secrets):
		raise click.UsageError('Please setup credentials before login in. Use spotify config --help for help')
	# Load user credentials from file system
	with open(cli_secrets) as cli_secrets_file:
		json_data = json.load(cli_secrets_file)
		if not json_data['client_key'] or not json_data['client_secret']:
			raise click.ClickException('There was a problem with your credentials, please run config command')
		return json_data['client_key'], json_data['client_secret']

if __name__ == "__main__":
	main()