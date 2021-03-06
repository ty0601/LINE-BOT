import message_json
from transitions.extensions import GraphMachine
from utils import send_flex_message
from api import get_coin_price, get_coin_metadata

curr_coin = {}


class TocMachine(GraphMachine):

    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_menu(self, event):
        text = event.message.text
        return text.lower() == "menu"

    def is_going_to_coin_menu(self, event):
        global curr_coin
        curr_coin[event.source.user_id] = event.message.text.lower()
        return True

    def is_going_to_choose_coins(self, event):
        text = event.message.text
        return 'coins' in text.lower()

    def is_going_to_price(self, event):
        text = event.message.text
        return text.lower() == "price"

    def is_going_to_metadata(self, event):
        text = event.message.text
        return text.lower() == "metadata"

    def is_going_to_fsm_graph(self, event):
        text = event.message.text
        return text.lower() == "show fsm graph"

    def is_going_to_introduction(self, event):
        text = event.message.text
        return text.lower() == "show introduction"

    def is_going_to_cancel(self, event):
        text = event.message.text
        return text.lower() == "end operation"

    def on_enter_menu(self, event):
        reply_token = event.reply_token
        send_flex_message(reply_token, "open menu", message_json.main_menu)

    def on_enter_choose_coins(self, event):
        global curr_coin
        curr_coin[event.source.user_id] = ''
        reply_token = event.reply_token
        send_flex_message(reply_token, "choose coin", message_json.choose_coin)

    def on_enter_coin_menu(self, event):
        reply_token = event.reply_token
        send_flex_message(reply_token, "coin menu", message_json.coin_menu)

    def on_enter_price(self, event):
        global curr_coin
        reply_token = event.reply_token
        coin_price = get_coin_price(curr_coin[event.source.user_id])
        if not coin_price:
            send_flex_message(reply_token, "not found", message_json.not_found_coin_menu)
        else:
            buffer = message_json.price_info
            buffer['body']['contents'][0]['contents'][0]['text'] = str(coin_price[0]) + ' - (' + str(
                coin_price[1]) + ')'
            buffer['body']['contents'][1]['contents'][1]['contents'][0]['text'] = '$ ' + str(coin_price[2])
            buffer['body']['contents'][2]['contents'][1]['contents'][0]['text'] = '$ ' + str(coin_price[3])
            buffer['body']['contents'][3]['contents'][1]['contents'][0]['text'] = '$ ' + str(coin_price[4])
            buffer['body']['contents'][4]['contents'][1]['contents'][0]['text'] = str(coin_price[5]) + '%'
            buffer['body']['contents'][5]['contents'][1]['contents'][0]['text'] = str(coin_price[6]) + '%'
            buffer['body']['contents'][6]['contents'][1]['contents'][0]['text'] = str(coin_price[7]) + '%'
            buffer['body']['contents'][7]['contents'][1]['contents'][0]['text'] = str(coin_price[8]) + '%'
            send_flex_message(reply_token, "coin price", buffer)

    def on_enter_metadata(self, event):
        global curr_coin
        reply_token = event.reply_token
        coin_data = get_coin_metadata(curr_coin[event.source.user_id])
        if not coin_data:
            send_flex_message(reply_token, "not found", message_json.not_found_coin_menu)
        else:
            buffer = message_json.metadata
            buffer['hero']['url'] = str(coin_data[0])
            buffer['body']['contents'][0]['text'] = str(coin_data[1]) + ' - (' + str(coin_data[2]) + ')'
            if not coin_data[3]:
                buffer['body']['contents'][1]['contents'][0]['contents'][1]['contents'][0][
                    'text'] = "CoinMarketCap Get More Detail"
                buffer['body']['contents'][1]['contents'][0]['contents'][1]['contents'][0]['action'][
                    'uri'] = "https://coinmarketcap.com/"
            else:
                buffer['body']['contents'][1]['contents'][0]['contents'][1]['contents'][0]['text'] = str(
                    coin_data[3][0])
                buffer['body']['contents'][1]['contents'][0]['contents'][1]['contents'][0]['action']['uri'] = str(
                    coin_data[3][0])
            if not coin_data[4]:
                buffer['body']['contents'][2]['contents'][0]['contents'][1]['contents'][0][
                    'text'] = "CoinMarketCap Get More Detail"
                buffer['body']['contents'][2]['contents'][0]['contents'][1]['contents'][0]['action'][
                    'uri'] = "https://coinmarketcap.com/"
            else:
                buffer['body']['contents'][2]['contents'][0]['contents'][1]['contents'][0]['text'] = str(
                    coin_data[4][0])
                buffer['body']['contents'][2]['contents'][0]['contents'][1]['contents'][0]['action']['uri'] = str(
                    coin_data[4][0])
            if not coin_data[5]:
                buffer['body']['contents'][3]['contents'][0]['contents'][1]['contents'][0][
                    'text'] = "CoinMarketCap Get More Detail"
                buffer['body']['contents'][3]['contents'][0]['contents'][1]['contents'][0]['action'][
                    'uri'] = "https://coinmarketcap.com/"
            else:
                buffer['body']['contents'][3]['contents'][0]['contents'][1]['contents'][0]['text'] = str(
                    coin_data[5][0])
                buffer['body']['contents'][3]['contents'][0]['contents'][1]['contents'][0]['action']['uri'] = str(
                    coin_data[5][0])
            send_flex_message(reply_token, "coin data", buffer)

    def on_enter_fsm_graph(self, event):
        reply_token = event.reply_token
        send_flex_message(reply_token, "not found", message_json.fsm_graph)
        self.go_back()

    def on_enter_introduction(self, event):
        reply_token = event.reply_token
        send_flex_message(reply_token, "open menu", message_json.introduction)
        self.go_back()

    def on_enter_cancel(self, event):
        reply_token = event.reply_token
        send_flex_message(reply_token, "cancel", message_json.cancel)
        self.go_back()
