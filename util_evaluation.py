class clf_dm_evaluation():
    sklearn = __import__('sklearn')
    pd = __import__('pandas')
    np = __import__('numpy')
    def __init__(self, in_clf):
        self.clf = in_clf

    def conf_matrix(self, array, real_class):
        return self.sklearn.metrics.confusion_matrix(real_class, self.clf.predict(array))

    def predict_error(self, array, real_class):
        conf_matrix = self.conf_matrix(array,real_class)
        return 'The corrected predicted percentage is: ' + str(round((conf_matrix[0,0]+conf_matrix[1,1])/conf_matrix.sum(),4)*100) + '%'

    def predict_prob_cut(self, array, real_class, cut=10, log=False):
        if log:
            try:
                prob_positive = self.clf.predict_log_proba(array)[:,1]
            except:
                raise Exception("Classifier do not have a predict_log_proba function......")
        else:
            try:
                prob_positive = self.clf.predict_proba(array)[:,1]
            except:
                raise Exception("Classifier do not have a predict_proba function......")

        try:
            pd_df = self.pd.DataFrame({'y_prob_a_1':prob_positive,
                                       'y_true_class': real_class,
                                       'y_prob_decile': self.pd.qcut(prob_positive,cut,labels=range(cut))})
        except:
            raise Exception("cannot cut")

        ret = self.pd.pivot_table(pd_df,
                                  values='y_true_class',
                                  index='y_prob_decile',
                                  aggfunc=lambda x:np.sum(x)/len(x))
        return ret

    def show_coef(self, array):
        ret = pd.DataFrame({'Col_name':array.columns, 'Coef': self.clf.coef_[0]}).sort_values('Col_name', ascending=False)
        return ret
