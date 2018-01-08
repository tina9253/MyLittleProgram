"""
pivot_gen - function that generate pivot table regarding ACQ_FLOW_FLAG and
ACQ_SALE_FLAG, for large sas dataset (SAS reader)
example input:
pivot_func_dict = {'ACQ_SALE_FLAG': [np.sum, len], 'ACQ_FLOW_FLAG': np.sum},
data_cols = ['Total Pop', 'Sales','Flows']
pivot_index = ['MB3G','MB3G_DESCRIPTION']
"""


class SasReaderPivot(object):
    """docstring for GeneratePivotTable."""
    pd = __import__('pandas')
    np = __import__('numpy')
    def __init__(self, df_reader, bins):
        """

        :type bins: a list specifying bins to group numerical variables
        """
        #super(SasReaderPivot, self).__init__()
        self.df_reader = df_reader
        self.bins = bins

    def generate_pivot(self,
                  pivot_index,
                  pivot_func_dict,
                  data_cols,
                  filters=None):
        ret = self.pd.DataFrame()
        for chunk in self.df_reader:
            piv = self._do_generate_pivot(chunk, pivot_index, pivot_func_dict, filters=filters)
            ret = self._merge_pivot_table(ret, piv, data_cols)
        return ret

    def _do_generate_pivot(self, data, pivot_index, pivot_func_dict, filters=None):
        # assert False, type(pivot_index)
        if not set(pivot_index).issubset(set(data.columns)):
            raise Exception('Wrong colnames in index')
        data = self._apply_filters(data, filters=filters)
        index, pivot_index = self._generate_category(data, pivot_index)
        return self.pd.pivot_table(data=data,
                            index=pivot_index,
                            values=pivot_func_dict.keys(),
                            aggfunc=pivot_func_dict,
                            fill_value=0)

    def _apply_filters(self, data, filters=None):
        # type: (pandas df, dictionary) -> new pandas df applying filters
        if not filters:
            return data
        if not set(list(filters.keys())).issubset(set(data.columns)):
            raise Exception('Wrong colnames in filters')
        filter_now = self.pd.Series()
        for key, value in filters.items():
            filter_now &=  [data.loc[row,key] in value for row in data.index]
            filter_index = data.index[filter_now]
        return data.loc[filter_index,:].reset_index(drop=True)

    def _generate_category(self, data, pivot_index):
        index = []
        pivot_index_mod = []
        for column in data[pivot_index].columns:
            if data[column].dtypes != 'float64':
                pivot_index_mod.append(column)
                continue
            new_name = column + '_grp'
            try:
                data[new_name] = self.pd.cut(data[column], self.bins, right=False)
            except:
                raise Exception('Cannot find bins. Please specify.')
            index.append(new_name)
            pivot_index_mod.append(new_name)
        return index, pivot_index_mod

    def _merge_pivot_table(self, original, pivot, data_cols):
        new_pivot = self.pd.concat([original, pivot], axis = 1).fillna(0)
        previous = new_pivot.iloc[:, 0:len(data_cols)]
        current = new_pivot.iloc[:, len(data_cols):]
        if current.shape[1]:
            new_pivot_array = self.np.add(self.np.array(previous), self.np.array(current))
        else:
            new_pivot_array = self.np.array(previous)
        return self.pd.DataFrame(new_pivot_array, index = new_pivot.index)
