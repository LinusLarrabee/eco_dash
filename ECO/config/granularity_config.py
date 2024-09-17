# config/granularity_config.py

granularity_options = {
    'controller': {
        'label': 'Per Controller',
        'value': 'controller',
        'path': {
            'wireless': 'controller_id/controller',
            'ethernet': 'controller_id/ethernet',
            'all': 'controller_id/controller/all'
        },
        'options': [
            {'label': 'Average RX Rate', 'value': 'average_rx_rate'},
            {'label': 'Average TX Rate', 'value': 'average_tx_rate'},
            {'label': 'Congestion Score', 'value': 'congestion_score'},
            {'label': 'Wi-Fi Coverage Score', 'value': 'wifi_coverage_score'},
            {'label': 'Noise', 'value': 'noise'},
            {'label': 'Error Rate', 'value': 'errors_rate'},
            {'label': 'WAN Bandwidth', 'value': 'wan_bandwidth'}
        ],
        'default': 'average_rx_rate'
    },
    'in-ap': {
        'label': 'Between Controller & Agent',
        'value': 'in-ap',
        'path': {
            'wireless': 'controller_id/non_controller',
            'ethernet': 'controller_id/non_controller',
            # 暂时无法获取有线backhaul的结果
            'all': 'controller_id/non_controller'
        },
        'options': [
            {'label': 'RSSI', 'value': 'backhaul_sta_rssi'},
            {'label': 'Link Rate', 'value': 'backhaul_sta_link_rate'}
        ],
        'default': 'backhaul_sta_rssi'
    }
}
