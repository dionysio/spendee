from uuid import uuid4
import datetime

from requests import Session
from requests.exceptions import RequestException

from .exceptions import SpendeeError


class Spendee(Session):
    def __init__(self, email: str, password: str, base_url: str = 'https://api.spendee.com/'):
        """
        :param email: user email to use for login
        :param password: user password to use for login
        :param base_url: base URL of the API
        """
        self.base_url = base_url
        self._email = email
        self._password = password

        self._api_uuid = None
        super(Spendee, self).__init__()

    def _build_url(self, version: str, url: str):
        """
        Builds the full URL for the Spendee API

        :param version: API version to use
        :param url: endpoint to user
        :rtype: str
        :return: full Spendee URL
        """
        return '{}{}/{}'.format(self.base_url, version, url)

    def request(self, method, url, version: str = 'v1', headers=None, params=None, **kwargs):
        """
        Adds additional functionality over super's request method:
        1. adds api-uuid header automatically for user-only methods
        2. adds error checking

        :param method: HTTP method to use
        :param url: endpoint to call
        :param version: API version to use. At the time of writing this, there were v1, v1.3, v1.4, v1.5, v1.6, v1.7, v1.8, v2
        :param headers: optional HTTP headers to use
        :param kwargs: additional arguments passed down to requests
        :rtype: dict
        :return:
        .. code-block:: json

            {
               "result":{

               },
               "version": "v1.4",
               "service": "api.user-login",
               "timestamp": "2019-12-29 07:30:01.163292",
               "status": "SUCCESS",
               "checksum": "addc3a80c74aa7268d14bee0209cc72a"
            }
        """
        if params is None:
            params = {
                'clientVersion': 'master',
                'clientPlatform': 'WEB'
            }
        if headers is None:
            headers = {}

        if url not in ('user-login', 'user-registration'):
            headers['api-uuid'] = self._get_api_uuid()

        url = self._build_url(version, url)

        response = None
        try:
            response = super(Spendee, self).request(method=method, url=url, headers=headers, params=params, **kwargs)
            response.raise_for_status()
        except RequestException as e:
            raise SpendeeError("Spendee returned a non-200 HTTP code.", response=response) from e

        try:
            result = response.json()
        except ValueError as e:
            raise SpendeeError("Response can't be serialized", response=response) from e

        if result.get('status') != 'SUCCESS':
            message = result.get('error', {}).get('message', 'Unexpected error on the Spendee side')
            raise SpendeeError(message, response=response)

        return result['result']

    ###

    def _get_api_uuid(self, **kwargs):
        """
        Retrieves api_uuid which is an auth token provided by self.user_login method and it's then sent in an api-uuid
        header in order to use authorized methods

        :return: UUID like "5808b3d4-9999-9999-8466-aad7f20b3252"
        :rtype: str
        """
        if not self._api_uuid:
            login = self.user_login(**kwargs)
            self._api_uuid = login['api_uuid']
        return self._api_uuid

    def user_registration(self, email: str = None, password: str = None, device_uuid: str = None,
                          categories_version: int = 2, with_categories: bool = True,  version: str = 'v1.5',
                          url: str = 'user-registration', **kwargs):
        """
        Sign up a new user

        :param email: user email
        :param password: user password
        :param device_uuid: random string with 36 characters, by default generates uuid4 hash
        :param categories_version: honestly not sure what this even does. 2 by default
        :param with_categories: same ^, enabled by default
        :rtype: dict
        :return:
        .. code-block:: json

            {
                "id":9999999,
                "uuid":"04fe4a6b-9999-9999-acac-fd2cbd660fb9",
                "email":"fry@planetexpress.com",
                "firstname":"",
                "lastname":"",
                "nickname":"",
                "timezone_id":null,
                "gender":null,
                "birth_date":null,
                "gp_uid":null,
                "fb_uid":null,
                "photo":null,
                "cohort_date":"2019-12-29 15:16:34",
                "categories_version":2,
                "referral_code":"44947b",
                "push_allowed":1,
                "past_type":null,
                "type":"free",
                "unconfirmed_email":null,
                "premium_expiration":null,
                "conditions_accepted":null,
                "global_currency":null,
                "last_recommendation_likelihood_date":null,
                "agreement_general_tos":"2019-12-29 15:16:34",
                "agreement_marketing":null,
                "viewed_tos_agreement_dialog":true,
                "viewed_dialogs":{
                    "transfers_feature_introduction":true
                },
                "has_already_tried_out_trial":false,
                "count_referred_users":0,
                "is_registered_via_referral_code":false,
                "api_uuid":"bbbf1c6f-9999-9999-86cd-89ec2632e8d5",
                "premium_operator":null,
                "user_referrer_name":null
            }
        """
        if device_uuid is None:
            device_uuid = str(uuid4())

        kwargs['json'] = {
            "email": email,
            "password": password,
            "categories_version": categories_version,
            "with_categories": with_categories,
            "device_uuid": device_uuid
        }

        return super(Spendee, self).post(url=url, version=version, **kwargs)

    def user_login(self, device_uuid: str = None, **kwargs):
        """
        Method to authenticate the user

        :param device_uuid: random string with 36 characters. Generates uuid4 by default
        :rtype: dict
        :return: the same as underlying self._user_login method
        """
        if device_uuid is None:
            device_uuid = str(uuid4())
        return self._user_login(email=self._email, password=self._password, device_uuid=device_uuid, **kwargs)

    def _user_login(self, email: str = None, password: str = None, device_uuid: str = None, version: str = 'v1.4',
                    url: str = 'user-login', **kwargs):
        """
        Method to authenticate the user

        :param email: user email
        :param password: user password
        :param device_uuid: random string with 36 characters
        :rtype: dict
        :return:
        .. code-block:: json

            {
                "id": 999999,
                "uuid": "b9b6ecb3-9999-9999-bf15-03fb802f4628",
                "email": "fry@planetexpress.com",
                "firstname": "Phillip J.",
                "lastname": "Fry",
                "nickname": "Fry",
                "timezone_id": "Europe/Prague",
                "gender": "male",
                "birth_date": "1974-08-14",
                "gp_uid": 107416106303948470000,b9
                "fb_uid": 107416104303448470000,
                "photo": "https://api.spendee.com/files/b/3/916307877cb8e1af749c70ed16271705",
                "cohort_date": "2017-10-19 18:03:59",
                "categories_version": 2,
                "referral_code": "53t71r",
                "push_allowed": 1,
                "past_type": "free",
                "type": "premium",
                "unconfirmed_email": null,
                "premium_expiration": "2020-01-02",
                "conditions_accepted": "2017-10-19 20:07:14",
                "global_currency": "EUR",
                "last_recommendation_likelihood_date": "2019-12-16 04:08:51.750837",
                "agreement_general_tos": "2019-11-24 22:54:56",
                "agreement_marketing": "2019-11-24 22:54:57",
                "viewed_tos_agreement_dialog": true,
                "viewed_dialogs":{
                    "black_friday_intro_2019": true,
                    "transfers_how_it_works": true,
                    "transfers_feature_introduction": true
                },
                "has_already_tried_out_trial": true,
                "count_referred_users": 0,
                "is_registered_via_referral_code": false,
                "api_uuid": "5808b3d4-9999-9999-8466-aad7f20b3252",
                "transactions_count": 7,
                "premium_operator": null
            }
        """
        kwargs['json'] = {
            'email': email,
            'password': password,
            'device_uuid': device_uuid
        }

        return super(Spendee, self).post(url=url, version=version, **kwargs)

    def user_logout(self, version: str = 'v1.4', url: str = 'user-logout', **kwargs):
        """
        Logout the user

        :rtype: bool
        :return: returns True if logout was successful
        """
        return super(Spendee, self).post(url=url, version=version, **kwargs)

    def user_get_profile(self, version: str = 'v1.4', url: str = 'user-get-profile', **kwargs):
        """
        Retrieve the user profile

        :rtype: dict
        :return:
        .. code-block:: json

            {
                "id": 999999,
                "uuid": "b9b6ecb3-9999-9999-bf15-03fb802f4628",
                "email": "fry@planetexpress.com",
                "firstname": "Phillip J.",
                "lastname": "Fry",
                "nickname": "Fry",
                "gender": "male",
                "gp_uid": 107416106303948470000,
                "fb_uid": 107416104303448470000,
                "photo": "https://api.spendee.com/files/b/3/916307877cb8e1af749c70ed16271705",
                "cohort_date": "2017-10-19 18:03:59",
                "categories_version": 2,
                "referral_code": "53t71r",
                "type": "premium",
                "unconfirmed_email": false,
                "timezone_id": null,
                "birth_date": "1974-08-14",
                "past_type": null,
                "premium_expiration": null,
                "conditions_accepted": "2017-10-19",
                "global_currency": "EUR",
                "agreement_general_tos": "2019-11-24 22:54:56",
                "agreement_marketing": "2019-11-24 22:54:57",
                "viewed_tos_agreement_dialog": true,
                "last_recommendation_likelihood_date": "2019-12-16",
                "viewed_dialogs":{
                    "black_friday_intro_2019": true,
                    "transfers_how_it_works": true,
                    "transfers_feature_introduction": true
                },
                "has_already_tried_out_trial": true,
                "count_referred_users": 0,
                "is_registered_via_referral_code": false,
                "introductory_offer_available": false,
                "geo":{
                    "continent": "North America",
                    "country": "United States",
                    "region": "New New York",
                    "city": "New New York"
                },
                "subscription_period": "MONTH",
                "product_id": "spendee.premium_banks.month_test4",
                "push_allowed": 1
            }
        """
        return self.post(url=url, version=version, **kwargs)

    def user_update_profile(self, firstname: str, lastname: str, email: str, gender: str, birth_date: datetime.date,
                            currency: str, photo: str, language_label: str, language_value: str, id: int,
                            version: str = 'v1.5', url: str = 'user-update-profile', **kwargs):
        """
        Update the user profile

        :param firstname: first name
        :param lastname: last name
        :param email: email address
        :param email: email address
        :param gender: male/female
        :param birth_date: birth date
        :param currency: EUR/USD...
        :param photo: URL of the image
        :param language_label: English/...
        :param language_value: en-US...
        :param id: user profile ID to update
        :rtype: dict
        :return:
        .. code-block:: json

            {
                "photo": "https://api.spendee.com/files/b/3/916307877cb8e1af749c70ed16271705"
            }
        """
        kwargs['json'] = {
            "lastname": lastname,
            "gender": gender,
            "birth_date": birth_date.strfmt('%Y-%m-%d'),
            "currency": currency,
            "photo": photo,
            "language": {"label": language_label, "value": language_value},
            "id": id,
            "firstname": firstname,
            "email": email
        }
        return self.post(url=url, version=version, **kwargs)

    def user_currencies(self, version: str = 'v1.6', url: str = 'user-currencies', **kwargs):
        """
        Retrieve all the currencies available

        :rtype: dict
        :return:
        .. code-block:: json

            {
                "recent": [
                  {
                    "code": "EUR",
                    "name": "Euro",
                    "decimal_digits": 2,
                    "usd_exchange_rate": "1.117469512638000",
                    "replaced_by": null,
                    "deleted_at": null
                  }
                ],
                "all": {
                  "currencies": [{
                      "code": "EUR",
                      "name": "Euro",
                      "decimal_digits": 2,
                      "usd_exchange_rate": "1.117469512638000",
                      "replaced_by": null,
                      "deleted_at": null
                  }]
                }
            }
        """
        return self.get(url=url, version=version, **kwargs)

    def get_all_user_categories(self, version: str = 'v1.6', url: str = 'get-all-user-categories', **kwargs):
        """
        Returns a list of all user defined categories

        :rtype: list
        :return:
        .. code-block:: json

            [{
                "id": 9999999,
                "name": "Flights",
                "wallet_id": null,
                "image_id": 2,
                "status": "active",
                "type": "expense",
                "position": 2,
                "color": "#F963A0",
                "modified": "2019-12-28 14:40:09.106943",
                "created": "2017-10-19 18:10:38.000000",
                "user_id": 999999,
                "word_id": null,
                "deletable": 0,
                "wallets_settings":[
                    {
                        "wallet_id": 9999999,
                        "category_id": 34958019,
                        "position": 2,
                        "visible": 1
                    }
                ],
                "transactions_stats":{
                    "affected_wallets_count": 1,
                    "total_count": 6,
                    "any_belongs_to_bank": false
                }
            }]
        """
        return self.get(url=url, version=version, **kwargs)

    ###

    def banks_get_all(self, version: str = 'v1.3', url: str = 'banks-get-all', **kwargs):
        """
        Returns a list of all connected bank accounts

        :rtype: list
        :return:
        .. code-block:: json

            [
                {
                    "id": 999999,
                    "provider_name": "\u010cSOB",
                    "provider_code": "csob_cz",
                    "provider_image": "https://api2.spendee.com/media/cache/provider_logo/salt-edge/csob_cz",
                    "remember_credentials": 0,
                    "last_fetch": "2017-10-19 18:10:37",
                    "refresh_possible": 0,
                    "country_code": "CZ",
                    "refresh_at": "2017-10-19 19:10:34",
                    "consent_expiration_date": null
                }
            ]
        """
        return self.get(url=url, version=version, **kwargs)

    def bank_login_detail(self, login_id: int, includeBank: bool = True, version: str = 'v2',
                          url: str = 'bankLogins/detail', **kwargs):
        """
        Get details of a bank account

        :param login_id:
        :param includeBank:
        :rtype: dict
        :return:
        .. code-block:: json

            {
                "provider":{
                  "name": "\u010cSOB",
                  "image": "https://api2.spendee.com/media/cache/provider_logo_original/csob_cz.png"
                },
                "accounts":[
                  {
                      "walletId": 9999999,
                      "nature": "account",
                      "id": 999999,
                      "accountNumber": "XXXXXXX",
                      "name": "Account",
                      "balance": 6.9299999999998,
                      "currency": "CZK",
                      "active": false
                  }
                ]
            }
        """
        kwargs['params'] = {
            'bankLoginId': login_id,
            'includeBank': 1 if includeBank else 0
        }
        return self.get(url=url, version=version, **kwargs)

    ###

    def wallet_get_all(self, version: str = 'v1', url: str = 'wallet-get-all', **kwargs):
        """
        Returns a list of all user's wallets

        :rtype: list
        :return:
        .. code-block:: json

            [
                {
                    "id": 9999999,
                    "uuid": "a197c99a-9999-9999-a027-0fb9509d5bbc",
                    "name": "Wallet",
                    "balance": 4.5000353099999,
                    "currency": "USD",
                    "status": "active",
                    "modified": "2019-12-28 15:12:08.905164",
                    "created": "2017-10-19 18:04:41.387892",
                    "starting_balance": 8.59,
                    "users_changed": "2019-12-28 15:19:14.626365",
                    "type": "default",
                    "is_free": false,
                    "last_opened": "2019-12-27 05:42:23",
                    "bank": null,
                    "sharing_users":[
                        {
                            "id": 999999,
                            "uuid": "b9b6ecb3-9999-9999-bf15-03fb802f4628",
                            "email": "fry@planetexpress.com",
                            "firstname": "Phillip J.",
                            "lastname": "Fry",
                            "nickname": "Fry",
                            "timezone_id": "Europe/Prague",
                            "gender": "male",
                            "birth_date": "1974-08-14",
                            "gp_uid": 107416104303448470000,
                            "fb_uid": 107416104303448470000,
                            "photo": "https://api.spendee.com//files/b/3/916307877cb8e1af749c70ed16271705",
                            "cohort_date": "2017-10-19 18:03:59",
                            "categories_version": 2,
                            "referral_code": "53t71r",
                            "is_owner": true
                        }
                    ],
                    "pending_users":[

                    ],
                    "invitation_emails":[

                    ],
                    "order": 0,
                    "include_future_transactions": true,
                    "visible_in_awo": true,
                    "is_visible": true,
                    "is_my": true
                }
            ]
        """
        return self.post(url=url, version=version, **kwargs)

    def wallet_get_transactions(self, offset: int = 0, limit: int = 10000, version: str = 'v1.8',
                                url: str = 'wallet-get-transactions', **kwargs):
        """
        Retrieve all the transactions

        :param offset: pagination offset
        :param limit: pagination limit
        :rtype: dict
        :return:
        .. code-block:: json

            {
                "id": 999999999,
                "uuid": "446d7d15-9999-9999-8bf3-05225b9117d3",
                "name": null,
                "user_id": 999999,
                "wallet_id": 9999999,
                "category_id": 34957616,
                "amount": -7.817304,
                "repeat": "never",
                "reminder": "never",
                "status": "active",
                "modified": "2019-11-24 14:00:54.348598",
                "created": "2019-11-24 14:00:54.348598",
                "start_date": "2019-11-24 13:59:07",
                "offset": "+09:00",
                "location_id": null,
                "image": null,
                "note": "Angry Norwegian Anchovies",
                "note_changed": 0,
                "template_id": null,
                "recurring_date": null,
                "rebuild_date": null,
                "foreign_currency": "JPY",
                "foreign_rate": 0.007171838494954,
                "foreign_amount": -1090,
                "is_pending": 0,
                "description": null,
                "timezone": "Asia/Tokyo",
                "linked_transaction_id": null,
                "type": "REGULAR",
                "hashtags": [],
                "transfer_type": null
            }

        """
        kwargs['json'] = {
            'offset': offset,
            'limit': limit
        }
        return self.post(url=url, version=version, **kwargs)

    def wallet_create(self, name: str, currency: str, order: int = 1, starting_balance: float = 0.00,
                      version: str = 'v1', url: str = 'wallet-create', **kwargs):
        """
        Create a wallet

        :param name: wallet name
        :param currency: currency to use
        :param order: wallet order position
        :param starting_balance: amount to start the wallet with

        :rtype: dict
        :return:
        .. code-block:: json

            {
                "id": 9999999,
                "uuid": "2ac71d51-9999-9999-9abb-da4476fc1b6c",
                "name": "Wallet Name",
                "balance": 1,
                "currency": "EUR",
                "status": "active",
                "modified": "2019-12-29 08:09:24.150933",
                "created": "2019-12-29 08:09:24.150933",
                "starting_balance": 1,
                "users_changed": null,
                "type": "default",
                "is_free": false,
                "last_opened": null,
                "bank": null,
                "categories":[],
                "transactions":[],
                "sharing_users":[
                    {
                        "id": 999999,
                        "uuid": "b9b6ecb3-9999-9999-bf15-03fb802f4628",
                        "email": "fry@planetexpress.com",
                        "firstname": "Phillip J.",
                        "lastname": "Fry",
                        "nickname": "Fry",
                        "timezone_id": "Europe/Prague",
                        "gender": "male",
                        "birth_date": "1974-08-14",
                        "gp_uid": 10741999930344847000,
                        "fb_uid": null,
                        "photo": "https://api.spendee.com//files/b/3/916307877cb8e1af749c70ed16271705",
                        "cohort_date": "2017-10-19 18:03:59",
                        "categories_version": 2,
                        "referral_code": "53t71r",
                        "is_owner": true
                    }
                ],
                "pending_users":[],
                "invitation_emails":[]
            }
        """
        kwargs['json'] = {
            'name': name,
            'starting_balance': starting_balance,
            'currency': currency,
            'order': order
        }
        return self.post(url=url, version=version, **kwargs)

    def wallet_update(self, id: int, name: str, currency: str, starting_balance: float = 0.00,
                      version: str = 'v1', url: str = 'wallet-update', **kwargs):
        """
        Update the wallet settings

        :param id: ID of the wallet to update
        :param name: new name of the wallet
        :param currency: new currency of the wallet
        :param starting_balance: new starting amount of the wallet
        :rtype: bool
        :return: returns True if wallet was updated successfully
        """
        kwargs['json'] = {
            "id": id,
            "name": name,
            "starting_balance": starting_balance,
            "currency": currency
        }
        return self.post(url=url, version=version, **kwargs)

    def wallet_delete(self, wallet_id: int, version: str = 'v1', url: str = 'wallet-delete', **kwargs):
        """
        Delete a wallet

        :param wallet_id: ID of the wallet to delete
        :rtype: bool
        :return: returns True if wallet was deleted successfully
        """
        kwargs['json'] = {
            'wallet_id': wallet_id
        }
        return self.post(url=url, version=version, **kwargs)

    def wallet_invite_to_share(self, wallet_id: int, emails: list, version: str = 'v1', url: str = 'wallet-invite-to-share', **kwargs):
        """
        Invite to share a wallet with another user

        :param wallet_id: ID of the wallet to share
        :param emails: list of emails to invite
        :rtype: bool
        :return: returns True if invitation has been sent successfully
        """
        if not isinstance(emails, list):
            emails = [emails]
        kwargs['json'] = {
            "emails": emails,
            "wallet_id": wallet_id
        }
        return self.post(url=url, version=version, **kwargs)

    def wallet_unshare_user(self, wallet_id: int, emails: list, version: str = 'v1', url: str = 'wallet-unshare-user',
                            **kwargs):
        """
        Delete an invite to a wallet

        :param wallet_id: ID of the wallet to stop sharing
        :param emails: list of emails to delete the invites for
        :rtype: bool
        :return: returns True if an invitation has been deleted successfully
        """
        kwargs['json'] = {
            "emails": emails,
            "wallet_id": wallet_id
        }
        return self.post(url=url, version=version, **kwargs)

    def wallet_create_category(self, name: str, wallet_id: int = None, image_id: int = 1, visible: bool = True,
                               position: int = 1, color='#f5534b', status='active', type='expense', version: str = 'v1.4',
                               url: str = 'wallet-create-category', **kwargs):
        """
        Create a category

        :param name: Name of the category
        :param wallet_id: Wallet this category is associated with
        :param image_id: image ID to use as an icon. You can retrieve the IDs from category_image_ids
        :param visible: whether it's visible. Enabled by default
        :param position: position of its order among other categories
        :param color: hex string of the color for the icon
        :param status: active
        :param type: expense/income
        :return: category_id
        :rtype: int
        """

        kwargs['json'] = {
            "name": name,
            "type": type,
            "image_id": image_id,
            "color": color,
            "status": status,
            "wallets_settings": [{
                "wallet_id": wallet_id,
                "visible": 1 if visible else 0,
                "position": position
            }]
        }
        return self.post(url=url, version=version, **kwargs)

    def wallet_delete_category(self, category_id: int, version: str = 'v1', url: str = 'wallet-delete-category', **kwargs):
        """
        Delete a category

        :param category_id: ID of the category to delete
        """
        kwargs['json'] = {
            "category_id": category_id
        }
        return self.post(url=url, version=version, **kwargs)

    def wallet_update_category(self, id: int, wallet_id: int, name: str, visible: bool = True, color: str = '#f5534b',
                               position: int = 1, image_id: int = 1, version: str = 'v1.4',
                               url: str = 'wallet-update-category', **kwargs):
        """
        Update category

        :param name: Name of the category
        :param wallet_id: Wallet this category is associated with
        :param image_id: image ID to use as an icon. You can retrieve the IDs from category_image_ids
        :param visible: whether it's visible. Enabled by default
        :param position: position of its order among other categories
        :param color: hex string of the color for the icon
        :return: True if category was updated successfully
        :rtype: bool
        """
        kwargs['json'] = {
            "name": name,
            "image_id": image_id,
            "color": color,
            "id": id,
            "wallet_id": wallet_id,
            "wallets_settings": [{"position": position, "visible": visible, "wallet_id": wallet_id}]
        }
        return self.post(url=url, version=version, **kwargs)

    ###

    def get_budgets(self, version: str = 'v1.7', url: str = 'get-budgets', **kwargs):
        """
        Retrieves a list of user's budgets

        :rtype: list
        :return:
        .. code-block:: json

            [{
                "id":999999,
                "uuid":"bcee8565-9999-9999-81a7-d26d57ff9675",
                "name":"Long Trip",
                "limit":1000,
                "currency":"EUR",
                "notification":0,
                "start_date":"2019-12-01",
                "end_date":"2019-12-31",
                "period":"once",
                "status":"active",
                "position":1,
                "all_categories_selected":1,
                "all_users_selected":1,
                "all_wallets_selected":1,
                "categories":[],
                "users":[],
                "wallets":[]
            }]
        """
        return self.get(url=url, version=version, **kwargs)

    @staticmethod
    def _build_budget_request(name: str, limit: str, currency: str, wallets: list, categories: list, users: list,
                              position: int = 1, start_date: datetime.date = None, end_date: datetime.date = None,
                              status: str = 'active', all_categories_selected: bool = True, all_users_selected: bool = True,
                              all_wallets_selected: bool = True, period: str = 'monthly', offline: bool = False,
                              notification: bool = True):

        if start_date is None:
            start_date = datetime.datetime.today()
        if end_date is None and period == 'once':
            end_date = datetime.datetime.today() + datetime.timedelta(weeks=4)

        request = {
            "offline":  offline,
            "name": name,
            "limit": limit,
            "currency": currency,
            "wallets": wallets,
            "categories": categories,
            "users": users,
            "period": period,
            "start_date": start_date.strftime("%Y-%m-%d"),

            "all_categories_selected": 1 if all_categories_selected else 0,
            "all_users_selected": 1 if all_users_selected else 0,
            "all_wallets_selected": 1 if all_wallets_selected else 0,

            "status": status,
            "notification": notification,
            "position": position
        }

        if end_date:
            request['end_date'] = end_date

        return request

    def create_budget(self, name: str, limit: str, currency: str, wallets: list, categories: list, users: list,
                      position: int = 1, start_date: datetime.date = None, end_date: datetime.date = None,
                      status: str = 'active', all_categories_selected: bool = True, all_users_selected: bool = True,
                      all_wallets_selected: bool = True, period: str = 'monthly', offline: bool = False,
                      notification: bool = True,  version: str = 'v1.7', url: str = 'create-budget', **kwargs):
        """
        Create a budget

        :param name: name of the budget
        :param limit: the budget amount
        :param currency: amount's currency
        :param wallets: list of wallets this budget is relevant to
        :param categories: list of categories this budget is relevant to
        :param users: list of users this budget is shared with
        :param position: order position of the budget among all the budgets
        :param start_date: when
        :param end_date: when is the end of the budget. Only relevant when period='once'
        :param status: active
        :param period: once/daily/weekly/biweekly/monthly/yearly
        :param offline: whether it was created offline
        :param notification: whether to enable notifications for this budget
        :param all_categories_selected: whether all categories were selected or only a subset of them
        :param all_wallets_selected: whether all wallets were selected or only a subset of them
        :param all_users_selected: whether all users were selected or only a subset of them
        :return:
        .. code-block:: json

            [{
                "id":9999999,
                "uuid":"1485fbde-9999-9999-b719-cde2de40a91a",
                "name":"Big Trip",
                "limit":1000,
                "currency":"EUR",
                "notification":1,
                "start_date":"2019-12-01",
                "end_date":"2020-01-01",
                "period":"once",
                "status":"active",
                "position":1,
                "all_categories_selected":1,
                "all_users_selected":1,
                "all_wallets_selected":1,
                "categories":[999999],
                "users":[99999],
                "wallets":[999999]
            }]
        """
        kwargs['json'] = self._build_budget_request(name, limit, currency, wallets, categories, users, position,
                                                    start_date, end_date, status, all_categories_selected,
                                                    all_users_selected, all_wallets_selected, period, offline,
                                                    notification)

        return self.post(url=url, version=version, **kwargs)

    def edit_budget(self, name: str, limit: str, currency: str, wallets: list, categories: list, users: list,
                      position: int = 1, start_date: datetime.date = None, end_date: datetime.date = None,
                      status: str = 'active', all_categories_selected: bool = True, all_users_selected: bool = True,
                      all_wallets_selected: bool = True, period: str = 'monthly', offline: bool = False,
                      notification: bool = True, version: str = 'v1.7', url: str = 'edit-budget', **kwargs):
        """
        Edit a budget

        :param name: name of the budget
        :param limit: the budget amount
        :param currency: amount's currency
        :param wallets: list of wallets this budget is relevant to
        :param categories: list of categories this budget is relevant to
        :param users: list of users this budget is shared with
        :param position: order position of the budget among all the budgets
        :param start_date: when
        :param end_date: when is the end of the budget. Only relevant when period='once'
        :param status: active
        :param period: once/daily/weekly/biweekly/monthly/yearly
        :param offline: whether it was created offline
        :param notification: whether to enable notifications for this budget
        :param all_categories_selected: whether all categories were selected or only a subset of them
        :param all_wallets_selected: whether all wallets were selected or only a subset of them
        :param all_users_selected: whether all users were selected or only a subset of them
        :return:
        .. code-block:: json

            {
               "offline":false,
               "name":"test",
               "limit":100000,
               "currency":"EUR",
               "wallets":[
                  3701346,
                  3701650,
                  3985011,
                  3798485,
                  4023988,
                  3781423,
                  3702897,
                  3701651
               ],
               "categories":[
                  34957623,
                  84022999,
                  83784771,
                  86439902,
                  83168392,
                  34957999,
                  85507860,
                  34958019,
                  88157983,
                  34958005,
                  89822749,
                  84022998,
                  89822608,
                  83167932,
                  86439208
               ],
               "users":[
                  782471,
                  1769631
               ],
               "period":"month",
               "start_date":"2020-04-17",
               "id":1134489,
               "all_categories_selected":0,
               "all_users_selected":1,
               "all_wallets_selected":1,
               "status":"active",
               "notification":true,
               "position":2
            }
        """

        kwargs['json'] = self._build_budget_request(name, limit, currency, wallets, categories, users, position,
                                                    start_date, end_date, status, all_categories_selected,
                                                    all_users_selected, all_wallets_selected, period, offline,
                                                    notification)

        return self.post(url=url, version=version, **kwargs)

    def delete_budget(self, budgets: list, version: str = 'v1.7', url: str = 'delete-budget', **kwargs):
        """
        Deletes a list of budgets
        :param budgets: list of budgets to delete
        """
        kwargs['json'] = {
            "budgets": budgets
        }
        return self.post(url=url, version=version, **kwargs)

    ###

    def category_image_ids(self, version: str = 'v1.3', url: str = 'category-image-ids', **kwargs):
        """
        Retrieves a list of all IDs of category icons

        :rtype: list
        :return:
        .. code-block:: json

            [13, 10]
        """
        return self.post(url=url, version=version, **kwargs)

    def countries(self, version: str = 'v2', url: str = 'countries', **kwargs):
        """
        Retrieves a list of all available countries

        :rtype: list
        :return:
        .. code-block:: json

            [{
                "code": "ZM",
                "name": "Zambia"
            }]
        """
        return self.post(url=url, version=version, **kwargs)

    def get_transaction_templates(self, version: str = 'v1.8', url: str = 'get-transaction-templates', **kwargs):
        """
        Retrieves a list of scheduled/repeating transactions

        :rtype: list
        :return:
        .. code-block:: json
            [{
                "id":999999,
                "uuid":"4e6a9e9d-9999-9999-86ff-7e839f06c720",
                "type":"REGULAR",
                "user_id":99999,
                "wallet_id":99999,
                "wallet_currency":"USD",
                "category_id":99999,
                "amount":-9.934876,
                "foreign_currency":"EUR",
                "foreign_rate":1.1064235632813,
                "foreign_amount":-1.78,
                "repeat":"every month",
                "reminder":"never",
                "status":"active",
                "created":"2019-12-10 04:46:02.265221",
                "modified":"2019-12-10 04:46:02.265221",
                "start_date":"2019-12-07 04:41:43",
                "last_instance_date":"2019-12-07",
                "deletion_date":null,
                "end_date":null,
                "offset":"+07:00",
                "image":null,
                "timezone":"Asia\/Ho_Chi_Minh",
                "note":null,
                "target_wallet_id":null,
                "transfer_type":null,
                "linked_transaction_id":null,
                "linked_transaction_uuid":null,
                "hashtags":[]
            }]
        """
        return self.get(url=url, version=version, **kwargs)

    def sync_refresh(self, login_id: int, wallet_id: int, version: str = 'v2', url: str = 'logins/refresh', **kwargs):
        """
        :param login_id: bank login id
        :param login_id: wallet id
        :param client_version: default parameter
        :param client_platform: default parameter
        :return:
        .. code-block:: json
            {
                "url": "https:\/\/api2.spendee.com\/finish\/error?token=xxx"
            }

            or

            {
                "url": "https:\/\/api2.spendee.com\/wait?token=xxx"
            }
        """
        kwargs['json'] = {
            'loginId': login_id,
            "oAuthReturnUrl": "https://app.spendee.com/wallet/{}/transactions/sync-account/oauth-return".format(wallet_id)
        }
        return self.put(url=url, version=version, **kwargs)

    def providers(self, country: str, version: str = 'v2', url: str = 'providers', **kwargs):
        """
        Retrieves a list of all available providers of bank accounts in a country

        :param country: 2 letter country code
        :rtype: list
        :return:
        .. code-block:: json

        [
              {
                 "name":"Demo Bank",
                 "countryCode":"AF",
                 "providerCode":"demobank_xo",
                 "isFree":true,
                 "is_free":true,
                 "picture":"https:\/\/api2.spendee.com\/media\/cache\/provider_logo_original\/demobank_xo.jpeg",
                 "thumb_24":"https:\/\/api2.spendee.com\/media\/cache\/provider_logo_thumb_24\/demobank_xo.jpeg"
              }
        ]
        """
        kwargs['params'] = {
            'country': country
        }
        return self.get(url=url, version=version, **kwargs)

    def connect_bank_account(self, provider_code: str, server_account_picker: bool = False,
                             oauth_return_url: str = "https://app.spendee.com/dashboard/connect-bank/oauth-return",
                             version: str = 'v2', url: str = 'url', **kwargs):
        """
        Creates a wallet that auto syncs from your bank account

        :param provider_code: providerCode returned for a bank from `self.providers`
        :param server_account_picker: default parameter
        :param oauth_return_url: default parameter
        :rtype: list
        :return:
        .. code-block:: json
            {
               "url":"https:\/\/api2.spendee.com\/form\/connector:salt-edge:login-form?token=xxx"
            }
        """
        kwargs['json'] = {
            "provider_code": provider_code,
            "oauth_return_url": oauth_return_url,
            "server_account_picker": server_account_picker
        }
        return self.post(url=url, version=version, **kwargs)

    def choose_bank_account(self, accounts: list, version: str = 'v2', url: str = 'visible', **kwargs):
        """
        After connecting a bank account, some banks have sub-accounts (for different currencies, savings, checking etc.)

        :param accounts: list of chosen account IDs
        :rtype: bool
        :return: true
        """
        kwargs['json'] = {
            "accounts": [{'id': account, 'isVisible': True} for account in accounts]
        }
        return self.put(url=url, version=version, **kwargs)
