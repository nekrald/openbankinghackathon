import enablebanking
import datetime
import logging

import util


def alior_settings(redirect_url):
    return {
        "sandbox": True,
        "clientId": "ee2193f2-cd9e-4ff4-896a-1fc1cd7a4108",  # API client ID
        "clientSecret": "C2hD3mF8gS3kH0yM8wK4mG2gD5eV1vN0tC5pJ3jO1iY4fJ1wD2",
        "certPath": None,  # Path or URI QWAC certificate in PEM format
        "keyPath": None,  # Path or URI to QWAC certificate private key in PEM format
        "signKeyPath": None,  # Path or URI to QSeal certificate in PEM format
        "signPubKeySerial": None,  # Public serial key of the QSeal certificate located in signKeyPath
        "signFingerprint": None,
        "signCertUrl": None,
        "accessToken": None,
        "refreshToken": None,
        "consentId": None,
        "paymentAuthRedirectUri": redirect_url,  # URI where clients are redirected to after payment authorization.
        "paymentAuthState": "test"  # This value returned to paymentAuthRedirectUri after payment authorization.
    }


def kir_settings(redirect_url):
    raise NotImplemented


class APIWrapper:
        def __init__(self):
            self.bank2config = {
                    'Alior' : alior_settings,
                    'KIR'   : kir_settings
            }
            self.bank2redirect = {
                    'Alior' : 'http://localhost',
                    'KIR'   : 'https://enablebanking.com',
            }

        def getLoginURLandAPI(self, bank):
            assert bank in ["Alior", "KIR"], "Unknown bank!"
            settings = self.bank2config[bank]
            redirect = self.bank2redirect[bank]
            api_client = enablebanking.ApiClient(
                    bank, connector_settings=settings(redirect))
            auth_api = enablebanking.AuthApi(api_client)
            access = enablebanking.Access(
                valid_until=(datetime.datetime.now() + datetime.timedelta(days=89)).strftime('%Y-%m-%d'),
                balances=enablebanking.BalancesAccess(),
                transactions=enablebanking.TransactionsAccess()
            )
            auth_url = auth_api.get_auth(
                    response_type="code",  # OAuth2 response type
                    redirect_uri=redirect,  # redirect URI
                    scope=["aisp"],  # API scopes
                    access=access,
                    state="test"
            ).url  # state to pass to redirect URL
            return auth_url, redirect,  (api_client, auth_api)


        def getUserTokenAndAPI(self, bank, api_client, auth_api, redirected_url):
            redirect_begin = self.bank2redirect[bank]
            parsed_query = util.parse_redirected_url(redirected_url)
            token = auth_api.make_token(
                    grant_type="authorization_code",  # grant type, MUST be set to "authorization_code"
                    code=parsed_query.get("code"),
                    # The code received in the query string when redirected from authorization
                    redirect_uri=redirect_begin)
            logging.info("Token: %s", token)

            aisp_api = enablebanking.AISPApi(api_client)  # api_client has already accessToken and refreshToken applied after call to makeToken()
            return aisp_api, token


        def getUserAccounts(self, aisp_api):
            accounts = aisp_api.get_accounts()
            logging.info("Accounts info: %s", accounts)
            processed = [(account.account_id.iban) for account in accounts]
            return processed


        def getAccountTransactions(self, aisp_api, account_id):
            raw_transactions = aisp_api.get_account_transactions(account_id,
                    date_from=(datetime.datetime.now() - datetime.timedelta(days=89)).strftime(date_format),
                    date_to=datetime.datetime.now().strftime(date_format))
            return util.analyzeTransactions(raw_transactions)

        def getAccountBalance(self, aisp_api, account_id):
            raw_balance = aisp_api.get_account_balances(account_id)
            balance = float(raw_balance['balances'][0]['balance_amount']['amount'])
            currency = raw_balance['balances'][0]['balance_amount']['amount']['currency']
            return balance, currency


