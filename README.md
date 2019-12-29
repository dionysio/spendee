# Spendee

This is a package for interfacing with a wonderful [Spendee app](https://www.spendee.com/).

# Warning

No guarantees are provided here. If you wanna use it, go for it, but do know that the original API is undocumented and while it works at the time of writing, it might stop at any time. I'm not associated with Spendee in any way.

# Installation

1. Be Python 3.7+ ready
2. `pip install spendee`
3. Enjoy.

### Endpoints

This is a list of all endpoints I've discovered. So far only a subset is implemented:

- [ ] v1/exchange-rate
- [ ] v1.3/currencies
- [X] v1.6/user-currencies
- [X] v2/countries

- [ ] v1/notification-count-unread
- [ ] v1/notification-get-all
- [ ] v1/notification-set

- [ ] v1.5/user-fb-connect
- [ ] v1.5/user-google-connect
- [X] v1.5/user-registration
- [X] v1.5/user-update-profile
- [ ] v1/user-check-email
- [ ] v1/user-set-subscription
- [ ] v1.4/user-forgot-password
- [X] v1.4/user-get-profile
- [ ] v1.4/user-get-profiles
- [X] v1.4/user-login
- [X] v1.4/user-logout
- [ ] v1.4/user-password-change-confirmation
- [ ] v1.4/request-deletion
- [ ] v1.4/request-email-change
- [ ] v1.4/confirm-deletion
- [ ] v1.4/confirm-email-change

- [ ] v1/wallet-accept-sharing
- [X] v1/wallet-create
- [X] v1/wallet-delete
- [X] v1/wallet-delete-category
- [ ] v1/wallet-get
- [X] v1/wallet-get-all
- [ ] v1/wallet-get-category
- [ ] v1/wallet-get-users
- [X] v1/wallet-invite-to-share
- [ ] v1/wallet-order-categories
- [X] v1/wallet-unshare-user
- [X] v1/wallet-update

- [X] v1.3/banks-get-all
- [ ] v1.3/delete-bank-login

- [X] v1.3/category-image-ids

- [ ] v1.4/merge-categories
- [ ] v1.4/recommendation-likelihood

- [X] v1.4/wallet-create-category
- [ ] v1.4/wallet-get-categories
- [X] v1.4/wallet-update-category

- [ ] v1.5/change-to-two-way-transfer
- [ ] v1.5/delete-transfer-transaction
- [ ] v1.5/link-two-transactions-into-transfer
- [ ] v1.5/revert-transfer-to-regular-transaction
- [ ] v1.5/transaction-suggestions
- [ ] v1.5/transfer-funds
- [ ] v1.5/update-transfer
- [ ] v1.5/viewed-dialogs
- [ ] v1.5/wallet-create-transaction
- [ ] v1.5/wallet-delete-transaction
- [ ] v1.5/wallet-update-transaction
- [X] v1.6/get-all-user-categories
- [ ] v1.6/get-transactions
- [ ] v1.6/iframe-wallet-data?id=
- [ ] v1.6/reorder-wallets

- [X] v1.7/create-budget
- [ ] v1.7/delete-budget
- [ ] v1.7/edit-budget
- [X] v1.7/get-budgets
- [ ] v1.7/reorder-budgets

- [ ] v1.8/create-transaction-template
- [ ] v1.8/delete-transaction-template
- [X] v1.8/get-transaction-templates
- [ ] v1.6/wallet-get-transaction
- [X] v1.8/wallet-get-transactions

- [ ] v2/destroyCredentials
- [ ] v2/providers?country=
- [ ] v2/url?clientVersion=
- [ ] v2/visible
