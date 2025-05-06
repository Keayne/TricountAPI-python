from api import TricountAPI


if __name__ == "__main__":

    trapi = TricountAPI('tZqzdVuUqIcJBaTVmo')
    
    # Get members of the tricount
    users = trapi.get_users()
    print('Tricount users:', list(users.values()))

    # Get all expenses
    expenses = trapi.get_expenses()
    print('Total expenses:', sum(expenses))

    # Get per member expenses
    for id, name in users.items():
        user_expenses = trapi.get_expenses(user_id=id)
        print(f'{name} expenses:', sum(user_expenses))

