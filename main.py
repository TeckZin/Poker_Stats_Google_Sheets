
from google.oauth2.service_account import Credentials
import gspread
from gspread.cell import Cell



scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]


def get_player_in_date_game(date_list, player_list):
    game = {}
    take_date_data_flag = False
    for i in range(len(date_list)):
        date = date_list[i]
        if take_date_data_flag:
            if date not in game:
                game[date] = [player_list[i]]
            else:
                game[date].append(player_list[i])
        elif date == "Date":
            take_date_data_flag = True


    return game



def generate_profit_col(date_list, player_list, in_for_list, out_for_list, sheet):
    players = {}
    take_date_data_flag = False
    sheet.sheet1.batch_clear(["F:F"])

    formula = f'=ARRAYFORMULA(E4:E{len(player_list)} - D4:D{len(player_list)})'

    sheet.sheet1.update_acell('F4', formula)


    profit_list = sheet.sheet1.col_values(6)

    for i in range(len(player_list)):
        player = player_list[i]
        date = date_list[i]
        if take_date_data_flag:
            profit = profit_list[i]
            if player not in players:
                players[player] = [[date, float(profit)]]
            else:
               players[player].append([date, float(profit)])
        elif player == "Player":
            take_date_data_flag = True
            sheet.sheet1.update_cell(3,6, "Profit")





    return players


def generate_player_profit_table(date_list, player_date_profit, sheet):
    sheet.sheet1.batch_clear(["G:R"])


    cells = []
    for i, date in enumerate(date_list):
        cell = Cell(row=2 + i, col=7, value=date)
        cells.append(cell)

    sheet.sheet1.update_cells(cells)


    batch_data = []
    return_data = []
    col_index = 0
    for player, profit_date_list in player_date_profit.items():
        profit_data = [player] + [0.0] * (len(date_list)-2)
        for date, profit in profit_date_list:
            if date in date_list:
                date_index = date_list.index(date) - 1
                profit_data[date_index] = float(profit)
        return_data.append(profit_data)

        batch_data.append({
            'range': f'{chr(72 + col_index)}3:{chr(72 + col_index)}{len(date_list) + 2}',
            'values': [[p] for p in profit_data]
        })
        col_index += 1

    sheet.sheet1.batch_update(batch_data)
    return return_data

def generate_profit_sum_list(profit_data, date_list, player_list, sheet):
    profit_sum_data = []
    for player_profit_data in profit_data:
        new_sum_list = [player_profit_data[0]]
        cumulative_sum = 0.0
        for profit in player_profit_data[1:]:
            cumulative_sum += float(profit)
            new_sum_list.append(cumulative_sum)
        profit_sum_data.append(new_sum_list)



    sheet2 = sheet.get_worksheet(1)
    sheet2.batch_clear(["A:R"])

    cells = []
    for i, date in enumerate(date_list):
        cell = Cell(row=2 + i, col=2, value=date)
        cells.append(cell)

    sheet2.update_cells(cells)

    profit_sum_data = [list(col) for col in zip(*profit_sum_data)]

    cell_list = []
    for i, row in enumerate(profit_sum_data):
        for j, value in enumerate(row):
            cell_list.append(gspread.Cell(row=i+3, col=j+3, value=value))


    sheet2.update_cells(cell_list)


    return profit_sum_data

if __name__ == "__main__":

    creds = Credentials.from_service_account_file("credentails.json",
                                                  scopes=scopes)
    client = gspread.authorize(creds)

    sheet_id = "1zdrqdZJfmSmFoOcD9tdTpieLClWCzulSKW-UgKRUMsQ"

    sheet = client.open_by_key(sheet_id)

    date_list = sheet.sheet1.col_values(2)
    player_list = sheet.sheet1.col_values(3)


    in_for_list = sheet.sheet1.col_values(4)
    out_for_list = sheet.sheet1.col_values(5)


    # print(date_list)



    game = get_player_in_date_game(date_list, player_list)



    players = generate_profit_col(date_list, player_list, in_for_list, out_for_list, sheet)

    # print(players)
    seen = set()
    date_list = [x for x in date_list if not (x in seen or seen.add(x))]

    profit_data = generate_player_profit_table(date_list, players, sheet)
    print(profit_data)


    profit_sum_data = generate_profit_sum_list(profit_data,date_list,player_list, sheet)
    print(profit_sum_data)




