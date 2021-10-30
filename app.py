import csv

from bokeh.models.callbacks import CustomJS
from time_converter import epoch_hours_ago, epoch_to_date_hour, epoch_to_datetime
from scheduler import Scheduler
import threading
import os
import statistics
import time

from bokeh.layouts import column, gridplot, layout, row
from bokeh.models import CheckboxButtonGroup, ColumnDataSource, TableColumn, DataTable
from bokeh.plotting import figure, curdoc


TYPES = ["btceur", "btcusd"]


def _read_datapoints_with_time_range(type, start, end):
    directory = 'data/{}/'.format(type)
    Xs, Ys = [], []
    for filename in os.listdir(directory):
        # TODO: can make bucket finer granularity to /date/hour/minute/ for faster search
        if filename.endswith(".csv") and start <= filename[:-4] <= end:
            path = directory+filename
            with open(path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    Xs.append(epoch_to_datetime(int(row[0])))
                    Ys.append(float(row[1]))
    return Xs, Ys


def read_datapoints(types):
    curr_epoch = int(time.time())
    # TODO: don't need to pull 24h of data everytime. Instead, save data in memory or cache and only pull data of the latest hour
    hours_back_epoch = epoch_hours_ago(curr_epoch, hours=24)
    start, end = epoch_to_date_hour(
        hours_back_epoch), epoch_to_date_hour(curr_epoch)
    datapoins_per_type = {}
    for type in types:
        Xs, Ys = _read_datapoints_with_time_range(type, start, end)
        datapoins_per_type[type] = Xs, Ys
    return datapoins_per_type


def get_price_graphs(dps):
    ps = [None for _ in dps]
    i = 0
    for type, xy in dps.items():
        ps[i] = figure(x_axis_label='timestamp',
                       y_axis_label=type, y_range=(min(xy[1])*0.95, max(xy[1])*1.05), toolbar_location=None)
        ps[i].border_fill_color = 'white'
        ps[i].background_fill_color = 'white'
        ps[i].outline_line_color = None
        ps[i].grid.grid_line_color = None
        ps[i].line(dps[type][0], dps[type][1], legend_label=type, line_width=2)
        i += 1
    return ps


def get_std_with_rank(dps):
    std_dict = {type: statistics.stdev(xy[1]) for type, xy in dps.items()}
    sorted_std_list = sorted(std_dict.items(), key=lambda item: item[1])
    sorted_tuples = [(k, v, rank)
                     for rank, (k, v) in enumerate(sorted_std_list, start=1)]
    return sorted_tuples


def create_std_ranking_table(dps):
    sorted_std_with_rank = get_std_with_rank(dps)
    unzipped_list = list(zip(*sorted_std_with_rank))
    df = {
        'rank': unzipped_list[2],
        'type': unzipped_list[0],
        'std': unzipped_list[1],
    }
    source = ColumnDataSource(df)
    columns = [
        TableColumn(field='type', title='Type'),
        TableColumn(field='std', title='Standard Deviation'),
        TableColumn(field='rank', title='Rank'),
    ]
    return DataTable(source=source, columns=columns)


def draw(dps):
    data_available = True
    for t, xy in dps.items():
        if xy[0] is None or xy[1] is None or len(xy[0]) <= 2 or len(xy[1]) <= 2:
            data_available = False
            break

    if not data_available:
        graph_row = row(
            figure(title="Data is not available now. Please refresh later ...", toolbar_location=None))
        curdoc().add_root(graph_row)
    else:
        graphs = get_price_graphs(dps)
        table = create_std_ranking_table(dps)
        graph_row = row(graphs[0], graphs[1])
        checkbox_button_group = CheckboxButtonGroup(
            labels=TYPES, active=[0, 1])
        checkbox_button_group.js_on_change('active', CustomJS(
            args=dict(plots=graphs, row=graph_row, checkbox=checkbox_button_group), code="""
                for (let i = 0; i < plots.length; i++){
                plots[i].visible = checkbox.active.includes(i)
            }
        """))
        price_tracking = layout([
            [checkbox_button_group],
            [graph_row, table],
        ])
        curdoc().add_root(price_tracking)


dps = read_datapoints(TYPES)
draw(dps)


def schedule_data_fetcher():
    scheduler = Scheduler()
    scheduler.register(TYPES[0], 10)  # get btceur data every 10 sec
    scheduler.register(TYPES[1], 10)
    scheduler.start()


thread = threading.Thread(target=schedule_data_fetcher, args=())
thread.daemon = True    # Daemonize thread
thread.start()          # Run in background
