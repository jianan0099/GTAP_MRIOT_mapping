import pickle


class HyperParas:
    def __init__(self):
        with open('raw_gtap_dataset/regions_list.pkl', 'rb') as f:
            self.regions_list = pickle.load(f)
        with open('raw_gtap_dataset/activities_list.pkl', 'rb') as f:
            self.activities_list = pickle.load(f)
        self.num_regions = len(self.regions_list)
        self.num_commodities = len(self.activities_list)
        self.num_items = self.num_regions * self.num_commodities
