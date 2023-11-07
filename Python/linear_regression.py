import attr

@attr.s()
class LinearRegression():
    data_points = attr.ib()

    def __attrs_post_init__(self):
        self._learn_data()

    def _learn_data(self, data_points=None):
        if isinstance(data_points, list):
            self.data_points = data_points

        x_list, y_list = [], []
        for x, y in self.data_points:
            x_list.append(x)
            y_list.append(y)
        x_mean = sum(x_list) / len(x_list)
        y_mean = sum(y_list) / len(y_list)

        top_sum = 0
        bottom_sum = 0
        for x, y in self.data_points:
            top_sum += (x - x_mean) * (y - y_mean)
            bottom_sum += (x - x_mean)**2

        self.slope = top_sum / bottom_sum
        self.y_intercept = y_mean - self.slope * x_mean

    def predict_x(self, y):
        return (y - self.y_intercept) / self.slope

    def predict_y(self, x):
        return self.slope * x + self.y_intercept
