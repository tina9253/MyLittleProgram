class dm_format():
    pd = __import__('pandas')
    np = __import__('numpy')
    def __init__(self, df_input=None):
        if df_input:
            self.well_ret = df_input
        else:
            self.well_ret = self.pd.DataFrame()
        self.colcnt = 0

    def _manage_flt_na_(self, data_col, zero_as_na=True, neg_as_na=True, na_item = None):
        if zero_as_na:
            data_col.replace(0,self.np.nan,inplace=True)
        if neg_as_na:
            data_col.loc[data_col<0] = self.np.nan
        if na_item:
            for item in na_item:
                data_col.replace(item,self.np.nan,inplace=True)
        return data_col

    def _manage_char_na_(self, data_col, na_item = None):
        if na_item:
            for item in na_item:
                data_col.replace(item,self.np.nan,inplace=True)
        else:
            raise Exception('NO designated missing value found....')
        return data_col

    def str_to_category(self, data_col, na_item=None, order=None):
        # to reduce data size
        if na_item:
            temp = self._manage_char_na_(data_col, na_item)
        else:
            temp = data_col

        ret = temp.astype('category')
        # If the category need to be ordered.
        if order:
            ret.cat.set_categories(list(order), ordered=True, inplace=True)
        self.well_ret['cate_'+ ret.name] = ret
        self.colcnt += 1
        return ret

    def str_to_dummy(self, data_col, na_item=None):
        if na_item:
            temp = self._manage_char_na_(data_col, na_item)
        else:
            temp = data_col

        ret = self.pd.get_dummies(temp,prefix=data_col.name)
        self.well_ret = self.pd.concat([self.well_ret,ret], axis=1)
        return ret

    def flt_to_int(self, data_col):
        self.well_ret['int_'+ data_col.name] = round(data_col)
        self.colcnt += 1
        return round(data_col)

    def str_to_flt(self, data_col):
        ret = data_col.astype('float64')
        self.well_ret['flt_'+data_col.name] = ret
        self.colcnt += 1
        return ret

    def sas_date(self, data_col):
        temp = self._manage_flt_na_(data_col)
        try:
            ret = self.pd.to_timedelta(temp, unit = 'D') + self.pd.datetime(1960,1,1)
            return ret
        except:
            raise Exception('Wrong sas_date format!')


    def sas_time(self, data_col):
        temp = self._manage_flt_na_(data_col)
        try:
            ret = self.pd.to_timedelta(temp, unit = 's') + self.pd.datetime(1960,1,1)
            return ret
        except:
            raise Exception('Wrong sas_date format!')

    def normalized_flt(self, data_col, ignore_na = False):
        if not ignore_na:
            temp = self._manage_flt_na_(data_col)
        else:
            temp = data_col
        ret = (temp - self.np.mean(temp))/self.np.std(temp)
        # remove outliers
        ret[abs(ret)>3] = self.np.nan
        ret_name = 'nrml' + data_col.name
        self.well_ret[ret_name] = ret
        self.colcnt += 1
        return ret

    def one_digit_trans_flt(self, data_col):
        temp = self._manage_flt_na_(data_col)
        factor = round(self.np.mean(self.np.log10(temp)))
        ret = temp/(10**factor)
        self.colcnt += 1
        self.well_ret[ret.name+'_X'+str(factor)] = ret
        return ret

    def cut_to_group_flt(self, data_col, cutpoint=None,labels=None):
        if len(cutpoint) != len(labels)+1: raise Exception('Labels length not consistent with cutpoint')
        ret = self.pd.cut(data_col, bins=cutpoint, labels=labels, include_lowest=True)
        self.colcnt += 1
        ret_name = 'cut_'+data_col.name
        self.well_ret[ret_name] = ret
        return ret

    def keep(self, data_col):
        self.well_ret[data_col.name] = data_col
        return data_col
