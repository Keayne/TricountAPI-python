# TricountAPI-python

A **read-only** Python wrapper for the undocumented Tricount API.  
This project is inspired by the [mlaily/TricountApi](https://github.com/mlaily/TricountApi) F# implementation, adapted and reimplemented in Python.


## Overview

Tricount is a popular app for sharing expenses within groups. This library allows you to programmatically fetch Tricount data such as members and expenses using the API endpoints used internally by the official app.

> ⚠️ Note: This API is undocumented and may change without notice. Use at your own risk. This wrapper currently supports **read-only** access and does not allow modifying data.


## Features

- Authenticate using a generated app installation ID and RSA key.
- Fetch tricount data for a given public identifier (tricount key).
- Access raw JSON data from the API.
- Extract user/member information (IDs and names).
- List all expenses or filter expenses by user ID.
- Refresh data on demand.


## Installation

Clone the repo or copy the `TricountAPI` class into your project.  
Requires the following dependencies:

- `requests`
- `cryptography`

Install dependencies with:

```bash
pip install requests cryptography
```


## Usage

```python
from tricount_api import TricountAPI

# Initialize with tricount public identifier token
trapi = TricountAPI(tricount_key="tZqzdVuUqIcJBaTVmo")

# Access raw JSON data
data = trapi.get_data()

# Get all users: dict of {user_id: user_name}
users = trapi.get_users()

# Get all expenses (list of amounts)
all_expenses = trapi.get_expenses()

# Get expenses filtered by user ID
user_id = list(users.keys())[0]
user_expenses = trapi.get_expenses(user_id=user_id)

# Update data by making a new API request
trapi.update_data()
```


## API Reference

```python3
TricountAPI(tricount_key: str, app_id: str = "")
```

Create a new instance.

- `tricount_key`: Public identifier token for the tricount, found in the tricount URL (e.g, https://tricount.com/tZqzdVuUqIcJBaTVmo).
- `app_id`: Optional fixed app installation ID to maintain consistent sessions. If omitted, a UUID will be generated.


#### Methods

- `get_data() -> dict`  
  Returns raw JSON data from the API.

- `get_users() -> dict`  
  Returns a dictionary mapping user IDs (as strings) to user names.

- `get_expenses(user_id: str = None) -> list`  
  Returns a list of expense amounts. If `user_id` is specified, only expenses related to that user are returned.

- `update_data() -> None`  
  Refreshes the data by requesting the API again.


## Credits

This Python implementation is inspired by and builds upon the work of [mlaily](https://github.com/mlaily), whose original F# implementation can be found [here](https://github.com/mlaily/TricountApi).  


## Disclaimer

Use of this library involves interacting with an official API that is not publicly documented or endorsed by Tricount. Be aware that endpoints or behaviors may change and break this wrapper. This wrapper does not support modifying data and should be used only for reading tricount information.


## License

MIT License
