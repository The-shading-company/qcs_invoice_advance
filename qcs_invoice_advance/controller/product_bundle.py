import frappe

def cal_cost(self, event):
    if self.items:
        tab = self.items
        avg_rate = []
        for i in range(0, len(tab)):
            avg_rate.append(tab[i].get("custom_cost"))
        self.custom_total_cost = sum(avg_rate)