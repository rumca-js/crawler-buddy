"""
Starts server at the specified location

Access through:
    ip:port/getj?url=.... etc.
"""
import socket
import shutil
import os
import tracemalloc
from datetime import datetime

from src import webtools
from src.server_init import create_app
from src.taskrunner import start_runner_thread
from commandlineparser import CommandLineParser


if __name__ == "__main__":
    app = create_app()
    
    p = CommandLineParser()
    p.parse()

    history_length = p.args.history_length
    if history_length:
        app.config['crawler_main'].container.set_records_size(history_length)
    if p.args.time_cache_minutes:
        app.config['crawler_main'].container.set_time_cache(p.args.time_cache_minutes)

    port = app.config['configuration'].get("port")
    host = app.config['configuration'].get("host")

    if p.args.trace:
        app.config['configuration'].set_trace()

    # TODO
    path = "storage"
    if os.path.exists(path):
        shutil.rmtree(path)

    # TODO?
    socket.setdefaulttimeout(100)

    if p.args.kill_processes and webtools.WebConfig.count_chrom_processes() > 0:
        print("Killing chrome processes")
        webtools.WebConfig.kill_chrom_processes()
        webtools.WebConfig.kill_xvfb_processes()
        print("Killing chrome processes DONE")

    webtools.WebConfig.disable_ssl_warnings()
    webtools.WebConfig.start_display()

    tracemalloc.start()

    if p.args.multi_process:
        thread, task_runner = start_runner_thread(container=app.config['crawler_main'].container, max_workers=app.config['configuration'].get_max_workers(), no_executor=False)
        app.config['crawler_main'].set_multi_process()
        app.config['task_runner'] = task_runner

    app.config['start_time'] = datetime.now()

    context = None
    if p.args.cert_file and p.args.cert_key:
        context = (p.args.cert_file, p.args.cert_key)

        app.run(
            debug=p.args.debug,
            host=host,
            port=port,
            threaded=True,
            ssl_context=context,
        )
    else:
        app.run(debug=True, host=host, port=port, threaded=True)

    webtools.WebConfig.stop_display()
