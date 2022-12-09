#type: ignore
class EmaxModel(Module):

    def __init__(self) -> None:
        super().__init__()
        self.theta_em = theta(150, bounds=(30, None))
        self.theta_et50 = theta(0.5, bounds=(0.01, None))
        self.eta_em = omega(0.09)
        self.eta_et50 = omega(0.09)
        self.eps = sigma(0.09)
        self.data = pd.read_csv(pathlib.Path(__file__).parent.joinpath('dataEmax.csv'))
        self.data = self.data[self.data['MDV'] == 0].reset_index()
        self.wt = covariate(self.data['WT'])
        self.height = covariate(self.data['HEIGHT'])

    def pred(self, t) -> tuple[Expression, Expression]:
        em = self.theta_em * (self.wt / 50) ** 0.75 * ff.exp(self.eta_em)
        em__wrt_theta_em = 0.053182958969449884 * self.wt ** 0.75 * __masmod__functional__exp(self.eta_em)
        em__wrt_theta_et50 = 0
        em__wrt_eta_em = 0.053182958969449884 * self.wt ** 0.75 * self.theta_em * __masmod__functional__exp(self.eta_em)
        em__wrt_eta_et50 = 0
        em__wrt_eps = 0
        __bool_1 = self.height > 180 and self.wt > 100 and (self.wt < 150)
        __bool_1__em = 0
        __bool_1__em__wrt_theta_em = 0.043734482957731115 * self.wt ** 0.8 * __masmod__functional__exp(self.eta_em)
        __bool_1__em__wrt_theta_et50 = 0
        __bool_1__em__wrt_eta_em = 0.043734482957731115 * self.wt ** 0.8 * self.theta_em * __masmod__functional__exp(self.eta_em)
        __bool_1__em__wrt_eta_et50 = 0
        __bool_1__em__wrt_eps = 0
        if __bool_1:
            __bool_1__em = self.theta_em * (self.wt / 50) ** 0.8 * ff.exp(self.eta_em)
        em = __bool_1 * __bool_1__em + (1 - __bool_1) * em
        em__wrt_theta_em = 0.053182958969449884 * self.wt ** 0.75 * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * __masmod__functional__exp(self.eta_em)
        em__wrt_theta_et50 = 0
        em__wrt_eta_em = 0.053182958969449884 * self.wt ** 0.75 * self.theta_em * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * self.theta_em * __masmod__functional__exp(self.eta_em)
        em__wrt_eta_et50 = 0
        em__wrt_eps = 0
        et = self.theta_et50 * ff.exp(self.eta_et50)
        et__wrt_theta_em = 0
        et__wrt_theta_et50 = __masmod__functional__exp(self.eta_et50)
        et__wrt_eta_em = 0
        et__wrt_eta_et50 = self.theta_et50 * __masmod__functional__exp(self.eta_et50)
        et__wrt_eps = 0
        effect = em * t / (et + t)
        effect__wrt_theta_em = t * (t + self.theta_et50 * __masmod__functional__exp(self.eta_et50)) ** -1 * (0.053182958969449884 * self.wt ** 0.75 * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * __masmod__functional__exp(self.eta_em))
        effect__wrt_theta_et50 = -1 * t * (t + self.theta_et50 * __masmod__functional__exp(self.eta_et50)) ** -2 * (0.053182958969449884 * self.wt ** 0.75 * self.theta_em * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * self.theta_em * __masmod__functional__exp(self.eta_em)) * __masmod__functional__exp(self.eta_et50)
        effect__wrt_eta_em = t * (t + self.theta_et50 * __masmod__functional__exp(self.eta_et50)) ** -1 * (0.053182958969449884 * self.wt ** 0.75 * self.theta_em * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * self.theta_em * __masmod__functional__exp(self.eta_em))
        effect__wrt_eta_et50 = -1 * t * self.theta_et50 * (t + self.theta_et50 * __masmod__functional__exp(self.eta_et50)) ** -2 * (0.053182958969449884 * self.wt ** 0.75 * self.theta_em * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * self.theta_em * __masmod__functional__exp(self.eta_em)) * __masmod__functional__exp(self.eta_et50)
        effect__wrt_eps = 0
        ipred = effect
        ipred__wrt_theta_em = t * (t + self.theta_et50 * __masmod__functional__exp(self.eta_et50)) ** -1 * (0.053182958969449884 * self.wt ** 0.75 * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * __masmod__functional__exp(self.eta_em))
        ipred__wrt_theta_et50 = -1 * t * (t + self.theta_et50 * __masmod__functional__exp(self.eta_et50)) ** -2 * (0.053182958969449884 * self.wt ** 0.75 * self.theta_em * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * self.theta_em * __masmod__functional__exp(self.eta_em)) * __masmod__functional__exp(self.eta_et50)
        ipred__wrt_eta_em = t * (t + self.theta_et50 * __masmod__functional__exp(self.eta_et50)) ** -1 * (0.053182958969449884 * self.wt ** 0.75 * self.theta_em * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * self.theta_em * __masmod__functional__exp(self.eta_em))
        ipred__wrt_eta_et50 = -1 * t * self.theta_et50 * (t + self.theta_et50 * __masmod__functional__exp(self.eta_et50)) ** -2 * (0.053182958969449884 * self.wt ** 0.75 * self.theta_em * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * self.theta_em * __masmod__functional__exp(self.eta_em)) * __masmod__functional__exp(self.eta_et50)
        ipred__wrt_eps = 0
        y = effect * (1 + self.eps)
        y__wrt_theta_em = t * (1 + self.eps) * (t + self.theta_et50 * __masmod__functional__exp(self.eta_et50)) ** -1 * (0.053182958969449884 * self.wt ** 0.75 * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * __masmod__functional__exp(self.eta_em))
        y__wrt_theta_et50 = -1 * t * (1 + self.eps) * (t + self.theta_et50 * __masmod__functional__exp(self.eta_et50)) ** -2 * (0.053182958969449884 * self.wt ** 0.75 * self.theta_em * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * self.theta_em * __masmod__functional__exp(self.eta_em)) * __masmod__functional__exp(self.eta_et50)
        y__wrt_eta_em = t * (1 + self.eps) * (t + self.theta_et50 * __masmod__functional__exp(self.eta_et50)) ** -1 * (0.053182958969449884 * self.wt ** 0.75 * self.theta_em * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * self.theta_em * __masmod__functional__exp(self.eta_em))
        y__wrt_eta_et50 = -1 * t * self.theta_et50 * (1 + self.eps) * (t + self.theta_et50 * __masmod__functional__exp(self.eta_et50)) ** -2 * (0.053182958969449884 * self.wt ** 0.75 * self.theta_em * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * self.theta_em * __masmod__functional__exp(self.eta_em)) * __masmod__functional__exp(self.eta_et50)
        y__wrt_eps = t * (t + self.theta_et50 * __masmod__functional__exp(self.eta_et50)) ** -1 * (0.053182958969449884 * self.wt ** 0.75 * self.theta_em * (1 + -1 * __bool_1) * __masmod__functional__exp(self.eta_em) + 0.043734482957731115 * self.wt ** 0.8 * __bool_1 * self.theta_em * __masmod__functional__exp(self.eta_em))
        return (ipred, y)