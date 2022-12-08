// Auto Generate at 2022-12-08 15:36:54.523009
#include <cmath>
#include <string>
#include <any>
#include <map>
#include <Eigen/Dense>
#include "masmod/libc/headers.hpp"

using std::exp;
using std::log;
using std::pow;
using masmod::libc::modules::IModule;

class __Module : public IModule
{
public:

// def pred(self, t) -> tuple[Expression, Expression]:
void pred(std::map<std::string, std::any>& self, double t, std::map<std::string, std::any>& __local, Eigen::VectorXd& __container)
{
double self__theta_em;
double self__theta_et50;
double self__eta_em;
double self__eta_et50;
double self__eps;
double self__wt;
double self__height;
int __bool_1;
double __else__bool_1__em;
double __bool_1__em;
double __bool_2;
double __else__bool_2__em;
double __bool_2__em;
double em;
double em__wrt_theta_em;
int em__wrt_theta_et50;
double em__wrt_eta_em;
int em__wrt_eta_et50;
int em__wrt_eps;
double et;
int et__wrt_theta_em;
double et__wrt_theta_et50;
int et__wrt_eta_em;
double et__wrt_eta_et50;
int et__wrt_eps;
double effect;
double effect__wrt_theta_em;
double effect__wrt_theta_et50;
double effect__wrt_eta_em;
double effect__wrt_eta_et50;
int effect__wrt_eps;
double ipred;
double ipred__wrt_theta_em;
double ipred__wrt_theta_et50;
double ipred__wrt_eta_em;
double ipred__wrt_eta_et50;
int ipred__wrt_eps;
double y;
double y__wrt_theta_em;
double y__wrt_theta_et50;
double y__wrt_eta_em;
double y__wrt_eta_et50;
double y__wrt_eps;

// #region 从 self context 获取变量值
// 变量
self__theta_em = std::any_cast<double>(self["theta_em"]);
self__theta_et50 = std::any_cast<double>(self["theta_et50"]);
self__eta_em = std::any_cast<double>(self["eta_em"]);
self__eta_et50 = std::any_cast<double>(self["eta_et50"]);
self__eps = std::any_cast<double>(self["eps"]);

// 数据集中的协变量
self__wt = std::any_cast<double>(self["wt"]);
self__height = std::any_cast<double>(self["height"]);
// #endregion

__bool_1 = self__height > 180;
__else__bool_1__em = 0;
__bool_1__em = 0;
__bool_2 = 0;
// if self.height > 180:
// if self.height > 180:
if (__bool_1)
{
__bool_2 = self__height > 200;
__else__bool_2__em = 0;
__bool_2__em = 0;
// if self.height > 200:
// if self.height > 200:
if (__bool_2)
{
// em = self.theta_em * (self.wt / 50)**0.75 * ff.exp(self.eta_em)
__bool_2__em = ((self__theta_em*pow((self__wt/50), 0.75))*exp(self__eta_em));
}
else {
// em = self.theta_em * (self.wt / 50)**0.8 * ff.exp(self.eta_em)
__else__bool_2__em = ((self__theta_em*pow((self__wt/50), 0.8))*exp(self__eta_em));
}
__bool_1__em = ((__bool_2*__bool_2__em)+((1-__bool_2)*__else__bool_2__em));
}
else {
// em = self.theta_em * (1 + self.eta_em)
__else__bool_1__em = (self__theta_em*(1+self__eta_em));
}
em = ((__bool_1*__bool_1__em)+((1-__bool_1)*__else__bool_1__em));
em__wrt_theta_em = ((__bool_1*((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*exp(self__eta_em))+(((0.043734482957731115*pow(self__wt, 0.8))*(1+(-1*__bool_2)))*exp(self__eta_em))))+((1+(-1*__bool_1))*(1+self__eta_em)));
em__wrt_theta_et50 = 0;
em__wrt_eta_em = ((__bool_1*(((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*self__theta_em)*exp(self__eta_em))+((((0.043734482957731115*pow(self__wt, 0.8))*self__theta_em)*(1+(-1*__bool_2)))*exp(self__eta_em))))+(self__theta_em*(1+(-1*__bool_1))));
em__wrt_eta_et50 = 0;
em__wrt_eps = 0;
// et = self.theta_et50 * ff.exp(self.eta_et50)
et = (self__theta_et50*exp(self__eta_et50));
et__wrt_theta_em = 0;
et__wrt_theta_et50 = exp(self__eta_et50);
et__wrt_eta_em = 0;
et__wrt_eta_et50 = (self__theta_et50*exp(self__eta_et50));
et__wrt_eps = 0;
// effect = em * t / (et + t)
effect = ((em*t)/(et+t));
effect__wrt_theta_em = ((t*pow((t+(self__theta_et50*exp(self__eta_et50))), -1))*((__bool_1*((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*exp(self__eta_em))+(((0.043734482957731115*pow(self__wt, 0.8))*(1+(-1*__bool_2)))*exp(self__eta_em))))+((1+(-1*__bool_1))*(1+self__eta_em))));
effect__wrt_theta_et50 = ((((-1*t)*pow((t+(self__theta_et50*exp(self__eta_et50))), -2))*((__bool_1*(((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*self__theta_em)*exp(self__eta_em))+((((0.043734482957731115*pow(self__wt, 0.8))*self__theta_em)*(1+(-1*__bool_2)))*exp(self__eta_em))))+((self__theta_em*(1+(-1*__bool_1)))*(1+self__eta_em))))*exp(self__eta_et50));
effect__wrt_eta_em = ((t*pow((t+(self__theta_et50*exp(self__eta_et50))), -1))*((__bool_1*(((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*self__theta_em)*exp(self__eta_em))+((((0.043734482957731115*pow(self__wt, 0.8))*self__theta_em)*(1+(-1*__bool_2)))*exp(self__eta_em))))+(self__theta_em*(1+(-1*__bool_1)))));
effect__wrt_eta_et50 = (((((-1*t)*self__theta_et50)*pow((t+(self__theta_et50*exp(self__eta_et50))), -2))*((__bool_1*(((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*self__theta_em)*exp(self__eta_em))+((((0.043734482957731115*pow(self__wt, 0.8))*self__theta_em)*(1+(-1*__bool_2)))*exp(self__eta_em))))+((self__theta_em*(1+(-1*__bool_1)))*(1+self__eta_em))))*exp(self__eta_et50));
effect__wrt_eps = 0;
// ipred = effect
ipred = effect;
ipred__wrt_theta_em = ((t*pow((t+(self__theta_et50*exp(self__eta_et50))), -1))*((__bool_1*((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*exp(self__eta_em))+(((0.043734482957731115*pow(self__wt, 0.8))*(1+(-1*__bool_2)))*exp(self__eta_em))))+((1+(-1*__bool_1))*(1+self__eta_em))));
ipred__wrt_theta_et50 = ((((-1*t)*pow((t+(self__theta_et50*exp(self__eta_et50))), -2))*((__bool_1*(((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*self__theta_em)*exp(self__eta_em))+((((0.043734482957731115*pow(self__wt, 0.8))*self__theta_em)*(1+(-1*__bool_2)))*exp(self__eta_em))))+((self__theta_em*(1+(-1*__bool_1)))*(1+self__eta_em))))*exp(self__eta_et50));
ipred__wrt_eta_em = ((t*pow((t+(self__theta_et50*exp(self__eta_et50))), -1))*((__bool_1*(((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*self__theta_em)*exp(self__eta_em))+((((0.043734482957731115*pow(self__wt, 0.8))*self__theta_em)*(1+(-1*__bool_2)))*exp(self__eta_em))))+(self__theta_em*(1+(-1*__bool_1)))));
ipred__wrt_eta_et50 = (((((-1*t)*self__theta_et50)*pow((t+(self__theta_et50*exp(self__eta_et50))), -2))*((__bool_1*(((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*self__theta_em)*exp(self__eta_em))+((((0.043734482957731115*pow(self__wt, 0.8))*self__theta_em)*(1+(-1*__bool_2)))*exp(self__eta_em))))+((self__theta_em*(1+(-1*__bool_1)))*(1+self__eta_em))))*exp(self__eta_et50));
ipred__wrt_eps = 0;
// y = effect * (1 + self.eps)
y = (effect*(1+self__eps));
y__wrt_theta_em = (((t*(1+self__eps))*pow((t+(self__theta_et50*exp(self__eta_et50))), -1))*((__bool_1*((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*exp(self__eta_em))+(((0.043734482957731115*pow(self__wt, 0.8))*(1+(-1*__bool_2)))*exp(self__eta_em))))+((1+(-1*__bool_1))*(1+self__eta_em))));
y__wrt_theta_et50 = (((((-1*t)*(1+self__eps))*pow((t+(self__theta_et50*exp(self__eta_et50))), -2))*((__bool_1*(((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*self__theta_em)*exp(self__eta_em))+((((0.043734482957731115*pow(self__wt, 0.8))*self__theta_em)*(1+(-1*__bool_2)))*exp(self__eta_em))))+((self__theta_em*(1+(-1*__bool_1)))*(1+self__eta_em))))*exp(self__eta_et50));
y__wrt_eta_em = (((t*(1+self__eps))*pow((t+(self__theta_et50*exp(self__eta_et50))), -1))*((__bool_1*(((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*self__theta_em)*exp(self__eta_em))+((((0.043734482957731115*pow(self__wt, 0.8))*self__theta_em)*(1+(-1*__bool_2)))*exp(self__eta_em))))+(self__theta_em*(1+(-1*__bool_1)))));
y__wrt_eta_et50 = ((((((-1*t)*self__theta_et50)*(1+self__eps))*pow((t+(self__theta_et50*exp(self__eta_et50))), -2))*((__bool_1*(((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*self__theta_em)*exp(self__eta_em))+((((0.043734482957731115*pow(self__wt, 0.8))*self__theta_em)*(1+(-1*__bool_2)))*exp(self__eta_em))))+((self__theta_em*(1+(-1*__bool_1)))*(1+self__eta_em))))*exp(self__eta_et50));
y__wrt_eps = ((t*pow((t+(self__theta_et50*exp(self__eta_et50))), -1))*((__bool_1*(((((0.053182958969449884*pow(self__wt, 0.75))*__bool_2)*self__theta_em)*exp(self__eta_em))+((((0.043734482957731115*pow(self__wt, 0.8))*self__theta_em)*(1+(-1*__bool_2)))*exp(self__eta_em))))+((self__theta_em*(1+(-1*__bool_1)))*(1+self__eta_em))));
// return ipred, y

// #region 将临时变量赋值至 context
__local["self__theta_em"] = self__theta_em;
__local["self__theta_et50"] = self__theta_et50;
__local["self__eta_em"] = self__eta_em;
__local["self__eta_et50"] = self__eta_et50;
__local["self__eps"] = self__eps;
__local["self__wt"] = self__wt;
__local["self__height"] = self__height;
__local["__bool_1"] = __bool_1;
__local["__else__bool_1__em"] = __else__bool_1__em;
__local["__bool_1__em"] = __bool_1__em;
__local["__bool_2"] = __bool_2;
__local["__else__bool_2__em"] = __else__bool_2__em;
__local["__bool_2__em"] = __bool_2__em;
__local["em"] = em;
__local["em__wrt_theta_em"] = em__wrt_theta_em;
__local["em__wrt_theta_et50"] = em__wrt_theta_et50;
__local["em__wrt_eta_em"] = em__wrt_eta_em;
__local["em__wrt_eta_et50"] = em__wrt_eta_et50;
__local["em__wrt_eps"] = em__wrt_eps;
__local["et"] = et;
__local["et__wrt_theta_em"] = et__wrt_theta_em;
__local["et__wrt_theta_et50"] = et__wrt_theta_et50;
__local["et__wrt_eta_em"] = et__wrt_eta_em;
__local["et__wrt_eta_et50"] = et__wrt_eta_et50;
__local["et__wrt_eps"] = et__wrt_eps;
__local["effect"] = effect;
__local["effect__wrt_theta_em"] = effect__wrt_theta_em;
__local["effect__wrt_theta_et50"] = effect__wrt_theta_et50;
__local["effect__wrt_eta_em"] = effect__wrt_eta_em;
__local["effect__wrt_eta_et50"] = effect__wrt_eta_et50;
__local["effect__wrt_eps"] = effect__wrt_eps;
__local["ipred"] = ipred;
__local["ipred__wrt_theta_em"] = ipred__wrt_theta_em;
__local["ipred__wrt_theta_et50"] = ipred__wrt_theta_et50;
__local["ipred__wrt_eta_em"] = ipred__wrt_eta_em;
__local["ipred__wrt_eta_et50"] = ipred__wrt_eta_et50;
__local["ipred__wrt_eps"] = ipred__wrt_eps;
__local["y"] = y;
__local["y__wrt_theta_em"] = y__wrt_theta_em;
__local["y__wrt_theta_et50"] = y__wrt_theta_et50;
__local["y__wrt_eta_em"] = y__wrt_eta_em;
__local["y__wrt_eta_et50"] = y__wrt_eta_et50;
__local["y__wrt_eps"] = y__wrt_eps;
// #endregion

// #region 将 reserved self attr 赋值至 __container
__container(0) = ipred;
__container(1) = y;
__container(2) = ipred__wrt_theta_em;
__container(3) = ipred__wrt_theta_et50;
__container(4) = ipred__wrt_eta_em;
__container(5) = ipred__wrt_eta_et50;
__container(6) = ipred__wrt_eps;
__container(7) = y__wrt_theta_em;
__container(8) = y__wrt_theta_et50;
__container(9) = y__wrt_eta_em;
__container(10) = y__wrt_eta_et50;
__container(11) = y__wrt_eps;
// #endregion
}
};

__DYLIB_EXPORT IModule* __dylib_module_factory()
{
return new __Module();
}
