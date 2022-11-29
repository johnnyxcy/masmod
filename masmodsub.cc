// Auto Generate at 2022-11-29 18:36:48.163538
#include <cmath>
#include <string>
#include <any>
#include <map>
#include <Eigen/Dense>

using std::exp;
using std::log;
using std::pow;



// #region 用户定义的变量
// def pred(self, t):
void pred(std::map<std::string, std::any>& self, double t, std::map<std::string, std::any>& __local, Eigen::VectorXd& __container)
// #endregion

{
double theta_em;
double theta_et50;
double eta_em;
double eta_et50;
double eps;
double em;
double __em_wrt_theta_em;
int __em_wrt_theta_et50;
double __em_wrt_eta_em;
int __em_wrt_eta_et50;
int __em_wrt_eps;
double et;
int __et_wrt_theta_em;
double __et_wrt_theta_et50;
int __et_wrt_eta_em;
double __et_wrt_eta_et50;
int __et_wrt_eps;
double effect;
double __effect_wrt_theta_em;
double __effect_wrt_theta_et50;
double __effect_wrt_eta_em;
double __effect_wrt_eta_et50;
int __effect_wrt_eps;
double ipred;
double __self_ipred_wrt_theta_em;
double __self_ipred_wrt_theta_et50;
double __self_ipred_wrt_eta_em;
double __self_ipred_wrt_eta_et50;
int __self_ipred_wrt_eps;
double y;
double __self_y_wrt_theta_em;
double __self_y_wrt_theta_et50;
double __self_y_wrt_eta_em;
double __self_y_wrt_eta_et50;
double __self_y_wrt_eps;

// #region 从 self context 获取变量值
theta_em = std::any_cast<double>(self["theta_em"]);
theta_et50 = std::any_cast<double>(self["theta_et50"]);
eta_em = std::any_cast<double>(self["eta_em"]);
eta_et50 = std::any_cast<double>(self["eta_et50"]);
eps = std::any_cast<double>(self["eps"]);
// #endregion

// em = self.theta_em * ff.exp(self.eta_em)
em = theta_em * exp(eta_em);
__em_wrt_theta_em = exp(eta_em);
__em_wrt_theta_et50 = 0;
__em_wrt_eta_em = theta_em * exp(eta_em);
__em_wrt_eta_et50 = 0;
__em_wrt_eps = 0;
// et = self.theta_et50 * ff.exp(self.eta_et50)
et = theta_et50 * exp(eta_et50);
__et_wrt_theta_em = 0;
__et_wrt_theta_et50 = exp(eta_et50);
__et_wrt_eta_em = 0;
__et_wrt_eta_et50 = theta_et50 * exp(eta_et50);
__et_wrt_eps = 0;
// effect = (em * t) / (et + t)
effect = em * t / et + t;
__effect_wrt_theta_em = t * exp(eta_em) / t + theta_et50 * exp(eta_et50);
__effect_wrt_theta_et50 = -t * theta_em * exp(eta_em) * exp(eta_et50) / pow(t + theta_et50 * exp(eta_et50), 2);
__effect_wrt_eta_em = t * theta_em * exp(eta_em) / t + theta_et50 * exp(eta_et50);
__effect_wrt_eta_et50 = -t * theta_em * theta_et50 * exp(eta_em) * exp(eta_et50) / pow(t + theta_et50 * exp(eta_et50), 2);
__effect_wrt_eps = 0;
// self.ipred = effect
ipred = effect;
__self_ipred_wrt_theta_em = t * exp(eta_em) / t + theta_et50 * exp(eta_et50);
__self_ipred_wrt_theta_et50 = -t * theta_em * exp(eta_em) * exp(eta_et50) / pow(t + theta_et50 * exp(eta_et50), 2);
__self_ipred_wrt_eta_em = t * theta_em * exp(eta_em) / t + theta_et50 * exp(eta_et50);
__self_ipred_wrt_eta_et50 = -t * theta_em * theta_et50 * exp(eta_em) * exp(eta_et50) / pow(t + theta_et50 * exp(eta_et50), 2);
__self_ipred_wrt_eps = 0;
// self.y = effect * (1 + self.eps)
y = effect * 1 + eps;
__self_y_wrt_theta_em = t * eps + 1 * exp(eta_em) / t + theta_et50 * exp(eta_et50);
__self_y_wrt_theta_et50 = -t * theta_em * eps + 1 * exp(eta_em) * exp(eta_et50) / pow(t + theta_et50 * exp(eta_et50), 2);
__self_y_wrt_eta_em = t * theta_em * eps + 1 * exp(eta_em) / t + theta_et50 * exp(eta_et50);
__self_y_wrt_eta_et50 = -t * theta_em * theta_et50 * eps + 1 * exp(eta_em) * exp(eta_et50) / pow(t + theta_et50 * exp(eta_et50), 2);
__self_y_wrt_eps = t * theta_em * exp(eta_em) / t + theta_et50 * exp(eta_et50);

// #region 将临时变量赋值至 context
__local["theta_em"] = theta_em;
__local["theta_et50"] = theta_et50;
__local["eta_em"] = eta_em;
__local["eta_et50"] = eta_et50;
__local["eps"] = eps;
__local["em"] = em;
__local["__em_wrt_theta_em"] = __em_wrt_theta_em;
__local["__em_wrt_theta_et50"] = __em_wrt_theta_et50;
__local["__em_wrt_eta_em"] = __em_wrt_eta_em;
__local["__em_wrt_eta_et50"] = __em_wrt_eta_et50;
__local["__em_wrt_eps"] = __em_wrt_eps;
__local["et"] = et;
__local["__et_wrt_theta_em"] = __et_wrt_theta_em;
__local["__et_wrt_theta_et50"] = __et_wrt_theta_et50;
__local["__et_wrt_eta_em"] = __et_wrt_eta_em;
__local["__et_wrt_eta_et50"] = __et_wrt_eta_et50;
__local["__et_wrt_eps"] = __et_wrt_eps;
__local["effect"] = effect;
__local["__effect_wrt_theta_em"] = __effect_wrt_theta_em;
__local["__effect_wrt_theta_et50"] = __effect_wrt_theta_et50;
__local["__effect_wrt_eta_em"] = __effect_wrt_eta_em;
__local["__effect_wrt_eta_et50"] = __effect_wrt_eta_et50;
__local["__effect_wrt_eps"] = __effect_wrt_eps;
__local["ipred"] = ipred;
__local["__self_ipred_wrt_theta_em"] = __self_ipred_wrt_theta_em;
__local["__self_ipred_wrt_theta_et50"] = __self_ipred_wrt_theta_et50;
__local["__self_ipred_wrt_eta_em"] = __self_ipred_wrt_eta_em;
__local["__self_ipred_wrt_eta_et50"] = __self_ipred_wrt_eta_et50;
__local["__self_ipred_wrt_eps"] = __self_ipred_wrt_eps;
__local["y"] = y;
__local["__self_y_wrt_theta_em"] = __self_y_wrt_theta_em;
__local["__self_y_wrt_theta_et50"] = __self_y_wrt_theta_et50;
__local["__self_y_wrt_eta_em"] = __self_y_wrt_eta_em;
__local["__self_y_wrt_eta_et50"] = __self_y_wrt_eta_et50;
__local["__self_y_wrt_eps"] = __self_y_wrt_eps;
// #endregion

// #region 将 reserved self attr 赋值至 __container
__container(0) = ipred
__container(1) = y
// #endregion

}