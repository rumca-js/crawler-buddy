import os
import psutil


class MemoryChecker(object):
    def __init__(self):
        self.memory_threshold = None
        self.start_memory = None

    def reset(self):
        self.start_memory = None

    def get_memory_usage(self):
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()

        # in bytes
        # print("RSS (Resident Set Size):", mem_info.rss)  # Actual physical memory used
        # print("VMS (Virtual Memory Size):", mem_info.vms)  # Total virtual_mb memory used
        # print(f"Memory used (RSS): {mem_info.rss / (1024 * 1024):.2f} MB")

        return mem_info

    def is_memory_limit_reached(self):
        memory_threshold = self.thread_memory_threshold
        if memory_threshold is None:
            return False

        memory = self.get_memory_usage()

        resident_mb = memory.rss / (1024 * 1024)
        virtual_mb = memory.vms / (1024 * 1024)

        if resident_mb > memory_threshold or virtual_mb > memory_threshold:
            return True
        return False

    def get_memory_increase(self):
        if self.start_memory is None:
            self.start_memory = self.get_memory_usage()
        else:
            current_memory = self.get_memory_usage()

            current_resident_mb = current_memory.rss / (1024 * 1024)
            current_virtual_mb = current_memory.vms / (1024 * 1024)

            start_resident_mb = self.start_memory.rss / (1024 * 1024)
            start_virtual_mb = self.start_memory.vms / (1024 * 1024)

            self.start_memory = current_memory

            if current_resident_mb > start_resident_mb:
                return current_resident_mb - start_resident_mb
            if current_virtual_mb > start_virtual_mb:
                return current_virtual_mb - start_virtual_mb

        return 0
