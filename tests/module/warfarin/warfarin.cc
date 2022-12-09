// Auto Generate at 2022-12-08 16:30:15.772851
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

// def pred(self, t: float) -> tuple[Expression, Expression]:
void pred(std::map<std::string, std::any>& self, double t, std::map<std::string, std::any>& __local, Eigen::VectorXd& __container)
{
double self__theta_V;
double self__theta_Cl;
double self__theta_ka;
double self__theta_alag;
double self__eta_Cl;
double self__eta_V;
double self__eta_ka;
double self__eta_alag;
double self__eps_prop;
double self__eps_add;
double self__dose;
double alag;
int alag__wrt_theta_V;
int alag__wrt_theta_Cl;
int alag__wrt_theta_ka;
double alag__wrt_theta_alag;
int alag__wrt_eta_Cl;
int alag__wrt_eta_V;
int alag__wrt_eta_ka;
double alag__wrt_eta_alag;
int alag__wrt_eps_prop;
int alag__wrt_eps_add;
double cl;
int cl__wrt_theta_V;
double cl__wrt_theta_Cl;
int cl__wrt_theta_ka;
int cl__wrt_theta_alag;
double cl__wrt_eta_Cl;
int cl__wrt_eta_V;
int cl__wrt_eta_ka;
int cl__wrt_eta_alag;
int cl__wrt_eps_prop;
int cl__wrt_eps_add;
double v;
double v__wrt_theta_V;
int v__wrt_theta_Cl;
int v__wrt_theta_ka;
int v__wrt_theta_alag;
int v__wrt_eta_Cl;
double v__wrt_eta_V;
int v__wrt_eta_ka;
int v__wrt_eta_alag;
int v__wrt_eps_prop;
int v__wrt_eps_add;
double ka;
int ka__wrt_theta_V;
int ka__wrt_theta_Cl;
double ka__wrt_theta_ka;
int ka__wrt_theta_alag;
int ka__wrt_eta_Cl;
int ka__wrt_eta_V;
double ka__wrt_eta_ka;
int ka__wrt_eta_alag;
int ka__wrt_eps_prop;
int ka__wrt_eps_add;
double k;
double k__wrt_theta_V;
double k__wrt_theta_Cl;
int k__wrt_theta_ka;
int k__wrt_theta_alag;
double k__wrt_eta_Cl;
double k__wrt_eta_V;
int k__wrt_eta_ka;
int k__wrt_eta_alag;
int k__wrt_eps_prop;
int k__wrt_eps_add;
int __bool_1;
double __else__bool_1__ipred;
double __bool_1__ipred;
double ipred;
double ipred__wrt_theta_V;
double ipred__wrt_theta_Cl;
double ipred__wrt_theta_ka;
double ipred__wrt_theta_alag;
double ipred__wrt_eta_Cl;
double ipred__wrt_eta_V;
double ipred__wrt_eta_ka;
double ipred__wrt_eta_alag;
int ipred__wrt_eps_prop;
int ipred__wrt_eps_add;
double y;
double y__wrt_theta_V;
double y__wrt_theta_Cl;
double y__wrt_theta_ka;
double y__wrt_theta_alag;
double y__wrt_eta_Cl;
double y__wrt_eta_V;
double y__wrt_eta_ka;
double y__wrt_eta_alag;
double y__wrt_eps_prop;
int y__wrt_eps_add;

// #region 从 self context 获取变量值
// 变量
self__theta_V = std::any_cast<double>(self["theta_V"]);
self__theta_Cl = std::any_cast<double>(self["theta_Cl"]);
self__theta_ka = std::any_cast<double>(self["theta_ka"]);
self__theta_alag = std::any_cast<double>(self["theta_alag"]);
self__eta_Cl = std::any_cast<double>(self["eta_Cl"]);
self__eta_V = std::any_cast<double>(self["eta_V"]);
self__eta_ka = std::any_cast<double>(self["eta_ka"]);
self__eta_alag = std::any_cast<double>(self["eta_alag"]);
self__eps_prop = std::any_cast<double>(self["eps_prop"]);
self__eps_add = std::any_cast<double>(self["eps_add"]);

// 数据集中的协变量
self__dose = std::any_cast<double>(self["dose"]);
// #endregion

// alag = self.theta_alag * exp(self.eta_alag)
alag = (self__theta_alag*exp(self__eta_alag));
alag__wrt_theta_V = 0;
alag__wrt_theta_Cl = 0;
alag__wrt_theta_ka = 0;
alag__wrt_theta_alag = exp(self__eta_alag);
alag__wrt_eta_Cl = 0;
alag__wrt_eta_V = 0;
alag__wrt_eta_ka = 0;
alag__wrt_eta_alag = (self__theta_alag*exp(self__eta_alag));
alag__wrt_eps_prop = 0;
alag__wrt_eps_add = 0;
// cl = self.theta_Cl * exp(self.eta_Cl)
cl = (self__theta_Cl*exp(self__eta_Cl));
cl__wrt_theta_V = 0;
cl__wrt_theta_Cl = exp(self__eta_Cl);
cl__wrt_theta_ka = 0;
cl__wrt_theta_alag = 0;
cl__wrt_eta_Cl = (self__theta_Cl*exp(self__eta_Cl));
cl__wrt_eta_V = 0;
cl__wrt_eta_ka = 0;
cl__wrt_eta_alag = 0;
cl__wrt_eps_prop = 0;
cl__wrt_eps_add = 0;
// v = self.theta_V * exp(self.eta_V)
v = (self__theta_V*exp(self__eta_V));
v__wrt_theta_V = exp(self__eta_V);
v__wrt_theta_Cl = 0;
v__wrt_theta_ka = 0;
v__wrt_theta_alag = 0;
v__wrt_eta_Cl = 0;
v__wrt_eta_V = (self__theta_V*exp(self__eta_V));
v__wrt_eta_ka = 0;
v__wrt_eta_alag = 0;
v__wrt_eps_prop = 0;
v__wrt_eps_add = 0;
// ka = self.theta_ka * exp(self.eta_ka)
ka = (self__theta_ka*exp(self__eta_ka));
ka__wrt_theta_V = 0;
ka__wrt_theta_Cl = 0;
ka__wrt_theta_ka = exp(self__eta_ka);
ka__wrt_theta_alag = 0;
ka__wrt_eta_Cl = 0;
ka__wrt_eta_V = 0;
ka__wrt_eta_ka = (self__theta_ka*exp(self__eta_ka));
ka__wrt_eta_alag = 0;
ka__wrt_eps_prop = 0;
ka__wrt_eps_add = 0;
// k = cl / v
k = (cl/v);
k__wrt_theta_V = ((((-1*self__theta_Cl)*pow(self__theta_V, -2))*exp(self__eta_Cl))*exp((-1*self__eta_V)));
k__wrt_theta_Cl = ((pow(self__theta_V, -1)*exp(self__eta_Cl))*exp((-1*self__eta_V)));
k__wrt_theta_ka = 0;
k__wrt_theta_alag = 0;
k__wrt_eta_Cl = (((self__theta_Cl*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)));
k__wrt_eta_V = ((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)));
k__wrt_eta_ka = 0;
k__wrt_eta_alag = 0;
k__wrt_eps_prop = 0;
k__wrt_eps_add = 0;
__bool_1 = alag > t;
__else__bool_1__ipred = 0;
__bool_1__ipred = 0;
// if alag > t:
// if alag > t:
if (__bool_1)
{
// ipred = 0
__bool_1__ipred = 0;
}
else {
// ipred = self.dose / v * ka / (ka - k) * (
__else__bool_1__ipred = ((((self__dose/v)*ka)/(ka-k))*(exp((-k*(t-alag)))-exp((-ka*(t-alag)))));
}
ipred = ((__bool_1*__bool_1__ipred)+((1-__bool_1)*__else__bool_1__ipred));
ipred__wrt_theta_V = ((((((((((-1*self__dose)*pow(self__theta_V, -2))*self__theta_ka)*(1+(-1*__bool_1)))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp((-1*self__eta_V)))*exp(self__eta_ka))+((((((((((-1*self__dose)*self__theta_Cl)*pow(self__theta_V, -3))*self__theta_ka)*(1+(-1*__bool_1)))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -2))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka)))+((((((((((self__dose*self__theta_Cl)*pow(self__theta_V, -3))*self__theta_ka)*(1+(-1*__bool_1)))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka))*exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))));
ipred__wrt_theta_Cl = (((((((((self__dose*pow(self__theta_V, -2))*self__theta_ka)*(1+(-1*__bool_1)))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -2))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka))+((((((((((-1*self__dose)*pow(self__theta_V, -2))*self__theta_ka)*(1+(-1*__bool_1)))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka))*exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))));
ipred__wrt_theta_ka = ((((((((self__dose*pow(self__theta_V, -1))*(1+(-1*__bool_1)))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp((-1*self__eta_V)))*exp(self__eta_ka))+((((((((-1*self__dose)*pow(self__theta_V, -1))*self__theta_ka)*(1+(-1*__bool_1)))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -2))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp((-1*self__eta_V)))*exp((2*self__eta_ka))))+((((((((self__dose*pow(self__theta_V, -1))*self__theta_ka)*(1+(-1*__bool_1)))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*exp((-1*self__eta_V)))*exp((2*self__eta_ka)))*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka)))));
ipred__wrt_theta_alag = (((((((self__dose*pow(self__theta_V, -1))*self__theta_ka)*(1+(-1*__bool_1)))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*(((((-1*self__theta_ka)*exp(self__eta_alag))*exp(self__eta_ka))*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+(((((self__theta_Cl*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))*exp(self__eta_alag))*exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V)))))))*exp((-1*self__eta_V)))*exp(self__eta_ka));
ipred__wrt_eta_Cl = ((((((((((self__dose*self__theta_Cl)*pow(self__theta_V, -2))*self__theta_ka)*(1+(-1*__bool_1)))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -2))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka))+(((((((((((-1*self__dose)*self__theta_Cl)*pow(self__theta_V, -2))*self__theta_ka)*(1+(-1*__bool_1)))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka))*exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))));
ipred__wrt_eta_V = ((((((((((-1*self__dose)*pow(self__theta_V, -1))*self__theta_ka)*(1+(-1*__bool_1)))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp((-1*self__eta_V)))*exp(self__eta_ka))+((((((((((-1*self__dose)*self__theta_Cl)*pow(self__theta_V, -2))*self__theta_ka)*(1+(-1*__bool_1)))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -2))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka)))+((((((((((self__dose*self__theta_Cl)*pow(self__theta_V, -2))*self__theta_ka)*(1+(-1*__bool_1)))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka))*exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))));
ipred__wrt_eta_ka = (((((((((self__dose*pow(self__theta_V, -1))*self__theta_ka)*(1+(-1*__bool_1)))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp((-1*self__eta_V)))*exp(self__eta_ka))+((((((((-1*self__dose)*pow(self__theta_V, -1))*pow(self__theta_ka, 2))*(1+(-1*__bool_1)))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -2))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp((-1*self__eta_V)))*exp((2*self__eta_ka))))+((((((((self__dose*pow(self__theta_V, -1))*pow(self__theta_ka, 2))*(1+(-1*__bool_1)))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*exp((-1*self__eta_V)))*exp((2*self__eta_ka)))*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka)))));
ipred__wrt_eta_alag = (((((((self__dose*pow(self__theta_V, -1))*self__theta_ka)*(1+(-1*__bool_1)))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*((((((-1*self__theta_alag)*self__theta_ka)*exp(self__eta_alag))*exp(self__eta_ka))*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+((((((self__theta_Cl*pow(self__theta_V, -1))*self__theta_alag)*exp(self__eta_Cl))*exp((-1*self__eta_V)))*exp(self__eta_alag))*exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V)))))))*exp((-1*self__eta_V)))*exp(self__eta_ka));
ipred__wrt_eps_prop = 0;
ipred__wrt_eps_add = 0;
// y = ipred * (1 + self.eps_prop) + self.eps_add
y = ((ipred*(1+self__eps_prop))+self__eps_add);
y__wrt_theta_V = (((((((((((-1*self__dose)*pow(self__theta_V, -2))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp((-1*self__eta_V)))*exp(self__eta_ka))+(((((((((((-1*self__dose)*self__theta_Cl)*pow(self__theta_V, -3))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -2))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka)))+(((((((((((self__dose*self__theta_Cl)*pow(self__theta_V, -3))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka))*exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))));
y__wrt_theta_Cl = ((((((((((self__dose*pow(self__theta_V, -2))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -2))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka))+(((((((((((-1*self__dose)*pow(self__theta_V, -2))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka))*exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))));
y__wrt_theta_ka = (((((((((self__dose*pow(self__theta_V, -1))*(1+(-1*__bool_1)))*(1+self__eps_prop))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp((-1*self__eta_V)))*exp(self__eta_ka))+(((((((((-1*self__dose)*pow(self__theta_V, -1))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -2))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp((-1*self__eta_V)))*exp((2*self__eta_ka))))+(((((((((self__dose*pow(self__theta_V, -1))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*exp((-1*self__eta_V)))*exp((2*self__eta_ka)))*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka)))));
y__wrt_theta_alag = ((((((((self__dose*pow(self__theta_V, -1))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*(((((-1*self__theta_ka)*exp(self__eta_alag))*exp(self__eta_ka))*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+(((((self__theta_Cl*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))*exp(self__eta_alag))*exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V)))))))*exp((-1*self__eta_V)))*exp(self__eta_ka));
y__wrt_eta_Cl = (((((((((((self__dose*self__theta_Cl)*pow(self__theta_V, -2))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -2))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka))+((((((((((((-1*self__dose)*self__theta_Cl)*pow(self__theta_V, -2))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka))*exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))));
y__wrt_eta_V = (((((((((((-1*self__dose)*pow(self__theta_V, -1))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp((-1*self__eta_V)))*exp(self__eta_ka))+(((((((((((-1*self__dose)*self__theta_Cl)*pow(self__theta_V, -2))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -2))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka)))+(((((((((((self__dose*self__theta_Cl)*pow(self__theta_V, -2))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*exp(self__eta_Cl))*exp(((-1*2)*self__eta_V)))*exp(self__eta_ka))*exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))));
y__wrt_eta_ka = ((((((((((self__dose*pow(self__theta_V, -1))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp((-1*self__eta_V)))*exp(self__eta_ka))+(((((((((-1*self__dose)*pow(self__theta_V, -1))*pow(self__theta_ka, 2))*(1+(-1*__bool_1)))*(1+self__eps_prop))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -2))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp((-1*self__eta_V)))*exp((2*self__eta_ka))))+(((((((((self__dose*pow(self__theta_V, -1))*pow(self__theta_ka, 2))*(1+(-1*__bool_1)))*(1+self__eps_prop))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*exp((-1*self__eta_V)))*exp((2*self__eta_ka)))*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka)))));
y__wrt_eta_alag = ((((((((self__dose*pow(self__theta_V, -1))*self__theta_ka)*(1+(-1*__bool_1)))*(1+self__eps_prop))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*((((((-1*self__theta_alag)*self__theta_ka)*exp(self__eta_alag))*exp(self__eta_ka))*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+((((((self__theta_Cl*pow(self__theta_V, -1))*self__theta_alag)*exp(self__eta_Cl))*exp((-1*self__eta_V)))*exp(self__eta_alag))*exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V)))))))*exp((-1*self__eta_V)))*exp(self__eta_ka));
y__wrt_eps_prop = (((((((self__dose*pow(self__theta_V, -1))*self__theta_ka)*(1+(-1*__bool_1)))*pow(((self__theta_ka*exp(self__eta_ka))+((((-1*self__theta_Cl)*pow(self__theta_V, -1))*exp(self__eta_Cl))*exp((-1*self__eta_V)))), -1))*((-1*exp((((-1*self__theta_ka)*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_ka))))+exp((((((-1*self__theta_Cl)*pow(self__theta_V, -1))*(t+((-1*self__theta_alag)*exp(self__eta_alag))))*exp(self__eta_Cl))*exp((-1*self__eta_V))))))*exp((-1*self__eta_V)))*exp(self__eta_ka));
y__wrt_eps_add = 1;
// return ipred, y

// #region 将临时变量赋值至 context
__local["self__theta_V"] = self__theta_V;
__local["self__theta_Cl"] = self__theta_Cl;
__local["self__theta_ka"] = self__theta_ka;
__local["self__theta_alag"] = self__theta_alag;
__local["self__eta_Cl"] = self__eta_Cl;
__local["self__eta_V"] = self__eta_V;
__local["self__eta_ka"] = self__eta_ka;
__local["self__eta_alag"] = self__eta_alag;
__local["self__eps_prop"] = self__eps_prop;
__local["self__eps_add"] = self__eps_add;
__local["self__dose"] = self__dose;
__local["alag"] = alag;
__local["alag__wrt_theta_V"] = alag__wrt_theta_V;
__local["alag__wrt_theta_Cl"] = alag__wrt_theta_Cl;
__local["alag__wrt_theta_ka"] = alag__wrt_theta_ka;
__local["alag__wrt_theta_alag"] = alag__wrt_theta_alag;
__local["alag__wrt_eta_Cl"] = alag__wrt_eta_Cl;
__local["alag__wrt_eta_V"] = alag__wrt_eta_V;
__local["alag__wrt_eta_ka"] = alag__wrt_eta_ka;
__local["alag__wrt_eta_alag"] = alag__wrt_eta_alag;
__local["alag__wrt_eps_prop"] = alag__wrt_eps_prop;
__local["alag__wrt_eps_add"] = alag__wrt_eps_add;
__local["cl"] = cl;
__local["cl__wrt_theta_V"] = cl__wrt_theta_V;
__local["cl__wrt_theta_Cl"] = cl__wrt_theta_Cl;
__local["cl__wrt_theta_ka"] = cl__wrt_theta_ka;
__local["cl__wrt_theta_alag"] = cl__wrt_theta_alag;
__local["cl__wrt_eta_Cl"] = cl__wrt_eta_Cl;
__local["cl__wrt_eta_V"] = cl__wrt_eta_V;
__local["cl__wrt_eta_ka"] = cl__wrt_eta_ka;
__local["cl__wrt_eta_alag"] = cl__wrt_eta_alag;
__local["cl__wrt_eps_prop"] = cl__wrt_eps_prop;
__local["cl__wrt_eps_add"] = cl__wrt_eps_add;
__local["v"] = v;
__local["v__wrt_theta_V"] = v__wrt_theta_V;
__local["v__wrt_theta_Cl"] = v__wrt_theta_Cl;
__local["v__wrt_theta_ka"] = v__wrt_theta_ka;
__local["v__wrt_theta_alag"] = v__wrt_theta_alag;
__local["v__wrt_eta_Cl"] = v__wrt_eta_Cl;
__local["v__wrt_eta_V"] = v__wrt_eta_V;
__local["v__wrt_eta_ka"] = v__wrt_eta_ka;
__local["v__wrt_eta_alag"] = v__wrt_eta_alag;
__local["v__wrt_eps_prop"] = v__wrt_eps_prop;
__local["v__wrt_eps_add"] = v__wrt_eps_add;
__local["ka"] = ka;
__local["ka__wrt_theta_V"] = ka__wrt_theta_V;
__local["ka__wrt_theta_Cl"] = ka__wrt_theta_Cl;
__local["ka__wrt_theta_ka"] = ka__wrt_theta_ka;
__local["ka__wrt_theta_alag"] = ka__wrt_theta_alag;
__local["ka__wrt_eta_Cl"] = ka__wrt_eta_Cl;
__local["ka__wrt_eta_V"] = ka__wrt_eta_V;
__local["ka__wrt_eta_ka"] = ka__wrt_eta_ka;
__local["ka__wrt_eta_alag"] = ka__wrt_eta_alag;
__local["ka__wrt_eps_prop"] = ka__wrt_eps_prop;
__local["ka__wrt_eps_add"] = ka__wrt_eps_add;
__local["k"] = k;
__local["k__wrt_theta_V"] = k__wrt_theta_V;
__local["k__wrt_theta_Cl"] = k__wrt_theta_Cl;
__local["k__wrt_theta_ka"] = k__wrt_theta_ka;
__local["k__wrt_theta_alag"] = k__wrt_theta_alag;
__local["k__wrt_eta_Cl"] = k__wrt_eta_Cl;
__local["k__wrt_eta_V"] = k__wrt_eta_V;
__local["k__wrt_eta_ka"] = k__wrt_eta_ka;
__local["k__wrt_eta_alag"] = k__wrt_eta_alag;
__local["k__wrt_eps_prop"] = k__wrt_eps_prop;
__local["k__wrt_eps_add"] = k__wrt_eps_add;
__local["__bool_1"] = __bool_1;
__local["__else__bool_1__ipred"] = __else__bool_1__ipred;
__local["__bool_1__ipred"] = __bool_1__ipred;
__local["ipred"] = ipred;
__local["ipred__wrt_theta_V"] = ipred__wrt_theta_V;
__local["ipred__wrt_theta_Cl"] = ipred__wrt_theta_Cl;
__local["ipred__wrt_theta_ka"] = ipred__wrt_theta_ka;
__local["ipred__wrt_theta_alag"] = ipred__wrt_theta_alag;
__local["ipred__wrt_eta_Cl"] = ipred__wrt_eta_Cl;
__local["ipred__wrt_eta_V"] = ipred__wrt_eta_V;
__local["ipred__wrt_eta_ka"] = ipred__wrt_eta_ka;
__local["ipred__wrt_eta_alag"] = ipred__wrt_eta_alag;
__local["ipred__wrt_eps_prop"] = ipred__wrt_eps_prop;
__local["ipred__wrt_eps_add"] = ipred__wrt_eps_add;
__local["y"] = y;
__local["y__wrt_theta_V"] = y__wrt_theta_V;
__local["y__wrt_theta_Cl"] = y__wrt_theta_Cl;
__local["y__wrt_theta_ka"] = y__wrt_theta_ka;
__local["y__wrt_theta_alag"] = y__wrt_theta_alag;
__local["y__wrt_eta_Cl"] = y__wrt_eta_Cl;
__local["y__wrt_eta_V"] = y__wrt_eta_V;
__local["y__wrt_eta_ka"] = y__wrt_eta_ka;
__local["y__wrt_eta_alag"] = y__wrt_eta_alag;
__local["y__wrt_eps_prop"] = y__wrt_eps_prop;
__local["y__wrt_eps_add"] = y__wrt_eps_add;
// #endregion

// #region 将 reserved self attr 赋值至 __container
__container(0) = ipred;
__container(1) = y;
__container(2) = ipred__wrt_theta_V;
__container(3) = ipred__wrt_theta_Cl;
__container(4) = ipred__wrt_theta_ka;
__container(5) = ipred__wrt_theta_alag;
__container(6) = ipred__wrt_eta_Cl;
__container(7) = ipred__wrt_eta_V;
__container(8) = ipred__wrt_eta_ka;
__container(9) = ipred__wrt_eta_alag;
__container(10) = ipred__wrt_eps_prop;
__container(11) = ipred__wrt_eps_add;
__container(12) = y__wrt_theta_V;
__container(13) = y__wrt_theta_Cl;
__container(14) = y__wrt_theta_ka;
__container(15) = y__wrt_theta_alag;
__container(16) = y__wrt_eta_Cl;
__container(17) = y__wrt_eta_V;
__container(18) = y__wrt_eta_ka;
__container(19) = y__wrt_eta_alag;
__container(20) = y__wrt_eps_prop;
__container(21) = y__wrt_eps_add;
// #endregion
}
};

__DYLIB_EXPORT IModule* __dylib_module_factory()
{
return new __Module();
}
