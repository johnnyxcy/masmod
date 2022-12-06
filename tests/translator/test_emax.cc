// Auto Generate at 2022-12-05 10:29:20.617356
#include <cmath>
#include <string>
#include <any>
#include <map>
#include <Eigen/Dense>
#include <vector>
#include <iostream>

using std::exp;
using std::log;
using std::pow;

// def pred(self, t):
void pred(std::map<std::string, std::any>& self, double t, std::map<std::string, std::any>& __local, Eigen::VectorXd& __container)
{
double __self__theta_em;
double __self__theta_et50;
double __self__eta_em;
double __self__eta_et50;
double __self__eps;
double __self__wt;
double __self__height;
bool __bool_1;
double __else__em;
double __bool_1__em;
double em;
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
double __self__ipred;
double __self__ipred_wrt_theta_em;
double __self__ipred_wrt_theta_et50;
double __self__ipred_wrt_eta_em;
double __self__ipred_wrt_eta_et50;
int __self__ipred_wrt_eps;
double __self__y;
double __self__y_wrt_theta_em;
double __self__y_wrt_theta_et50;
double __self__y_wrt_eta_em;
double __self__y_wrt_eta_et50;
double __self__y_wrt_eps;

// #region 从 self context 获取变量值
// 变量
__self__theta_em = std::any_cast<double>(self["theta_em"]);
__self__theta_et50 = std::any_cast<double>(self["theta_et50"]);
__self__eta_em = std::any_cast<double>(self["eta_em"]);
__self__eta_et50 = std::any_cast<double>(self["eta_et50"]);
__self__eps = std::any_cast<double>(self["eps"]);

// 数据集中的协变量
__self__wt = std::any_cast<double>(self["wt"]);
__self__height = std::any_cast<double>(self["height"]);
// #endregion

__bool_1 = __self__height > 180;
__else__em = 0;
__bool_1__em = 0;
// if self.height > 180:
// if self.height > 180:
if (__bool_1)
{
// em = self.theta_em * (1 + self.eta_em)
__bool_1__em = (__self__theta_em*(1+__self__eta_em));
}
else {
// em = self.theta_em * (self.wt / 50)**0.75 * ff.exp(self.eta_em)
__else__em = ((__self__theta_em*pow((__self__wt/50), 0.75))*exp(__self__eta_em));
}
em = ((0+((1*int(__bool_1))*__bool_1__em))+((1*(1-int(__bool_1)))*__else__em));
// et = self.theta_et50 * ff.exp(self.eta_et50)
et = (__self__theta_et50*exp(__self__eta_et50));
__et_wrt_theta_em = 0;
__et_wrt_theta_et50 = exp(__self__eta_et50);
__et_wrt_eta_em = 0;
__et_wrt_eta_et50 = (__self__theta_et50*exp(__self__eta_et50));
__et_wrt_eps = 0;
// effect = em * t / (et + t)
effect = ((em*t)/(et+t));
__effect_wrt_theta_em = ((t*pow(((0+t)+(__self__theta_et50*exp(__self__eta_et50))), -1))*((0+(__bool_1*((0+1)+__self__eta_em)))+(((0.053182958969449884*pow(__self__wt, 0.75))*((0+1)+(-1*__bool_1)))*exp(__self__eta_em))));
__effect_wrt_theta_et50 = ((((-1*t)*pow(((0+t)+(__self__theta_et50*exp(__self__eta_et50))), -2))*((0+((__bool_1*__self__theta_em)*((0+1)+__self__eta_em)))+((((0.053182958969449884*pow(__self__wt, 0.75))*__self__theta_em)*((0+1)+(-1*__bool_1)))*exp(__self__eta_em))))*exp(__self__eta_et50));
__effect_wrt_eta_em = ((t*pow(((0+t)+(__self__theta_et50*exp(__self__eta_et50))), -1))*((0+(__bool_1*__self__theta_em))+((((0.053182958969449884*pow(__self__wt, 0.75))*__self__theta_em)*((0+1)+(-1*__bool_1)))*exp(__self__eta_em))));
__effect_wrt_eta_et50 = (((((-1*t)*__self__theta_et50)*pow(((0+t)+(__self__theta_et50*exp(__self__eta_et50))), -2))*((0+((__bool_1*__self__theta_em)*((0+1)+__self__eta_em)))+((((0.053182958969449884*pow(__self__wt, 0.75))*__self__theta_em)*((0+1)+(-1*__bool_1)))*exp(__self__eta_em))))*exp(__self__eta_et50));
__effect_wrt_eps = 0;
// self.ipred = effect
__self__ipred = effect;
__self__ipred_wrt_theta_em = ((t*pow(((0+t)+(__self__theta_et50*exp(__self__eta_et50))), -1))*((0+(__bool_1*((0+1)+__self__eta_em)))+(((0.053182958969449884*pow(__self__wt, 0.75))*((0+1)+(-1*__bool_1)))*exp(__self__eta_em))));
__self__ipred_wrt_theta_et50 = ((((-1*t)*pow(((0+t)+(__self__theta_et50*exp(__self__eta_et50))), -2))*((0+((__bool_1*__self__theta_em)*((0+1)+__self__eta_em)))+((((0.053182958969449884*pow(__self__wt, 0.75))*__self__theta_em)*((0+1)+(-1*__bool_1)))*exp(__self__eta_em))))*exp(__self__eta_et50));
__self__ipred_wrt_eta_em = ((t*pow(((0+t)+(__self__theta_et50*exp(__self__eta_et50))), -1))*((0+(__bool_1*__self__theta_em))+((((0.053182958969449884*pow(__self__wt, 0.75))*__self__theta_em)*((0+1)+(-1*__bool_1)))*exp(__self__eta_em))));
__self__ipred_wrt_eta_et50 = (((((-1*t)*__self__theta_et50)*pow(((0+t)+(__self__theta_et50*exp(__self__eta_et50))), -2))*((0+((__bool_1*__self__theta_em)*((0+1)+__self__eta_em)))+((((0.053182958969449884*pow(__self__wt, 0.75))*__self__theta_em)*((0+1)+(-1*__bool_1)))*exp(__self__eta_em))))*exp(__self__eta_et50));
__self__ipred_wrt_eps = 0;
// self.y = effect * (1 + self.eps)
__self__y = (effect*(1+__self__eps));
__self__y_wrt_theta_em = (((t*((0+1)+__self__eps))*pow(((0+t)+(__self__theta_et50*exp(__self__eta_et50))), -1))*((0+(__bool_1*((0+1)+__self__eta_em)))+(((0.053182958969449884*pow(__self__wt, 0.75))*((0+1)+(-1*__bool_1)))*exp(__self__eta_em))));
__self__y_wrt_theta_et50 = (((((-1*t)*((0+1)+__self__eps))*pow(((0+t)+(__self__theta_et50*exp(__self__eta_et50))), -2))*((0+((__bool_1*__self__theta_em)*((0+1)+__self__eta_em)))+((((0.053182958969449884*pow(__self__wt, 0.75))*__self__theta_em)*((0+1)+(-1*__bool_1)))*exp(__self__eta_em))))*exp(__self__eta_et50));
__self__y_wrt_eta_em = (((t*((0+1)+__self__eps))*pow(((0+t)+(__self__theta_et50*exp(__self__eta_et50))), -1))*((0+(__bool_1*__self__theta_em))+((((0.053182958969449884*pow(__self__wt, 0.75))*__self__theta_em)*((0+1)+(-1*__bool_1)))*exp(__self__eta_em))));
__self__y_wrt_eta_et50 = ((((((-1*t)*__self__theta_et50)*((0+1)+__self__eps))*pow(((0+t)+(__self__theta_et50*exp(__self__eta_et50))), -2))*((0+((__bool_1*__self__theta_em)*((0+1)+__self__eta_em)))+((((0.053182958969449884*pow(__self__wt, 0.75))*__self__theta_em)*((0+1)+(-1*__bool_1)))*exp(__self__eta_em))))*exp(__self__eta_et50));
__self__y_wrt_eps = ((t*pow(((0+t)+(__self__theta_et50*exp(__self__eta_et50))), -1))*((0+((__bool_1*__self__theta_em)*((0+1)+__self__eta_em)))+((((0.053182958969449884*pow(__self__wt, 0.75))*__self__theta_em)*((0+1)+(-1*__bool_1)))*exp(__self__eta_em))));

// #region 将临时变量赋值至 context
__local["__self__theta_em"] = __self__theta_em;
__local["__self__theta_et50"] = __self__theta_et50;
__local["__self__eta_em"] = __self__eta_em;
__local["__self__eta_et50"] = __self__eta_et50;
__local["__self__eps"] = __self__eps;
__local["__self__wt"] = __self__wt;
__local["__self__height"] = __self__height;
__local["__bool_1"] = __bool_1;
__local["__else__em"] = __else__em;
__local["__bool_1__em"] = __bool_1__em;
__local["em"] = em;
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
__local["__self__ipred"] = __self__ipred;
__local["__self__ipred_wrt_theta_em"] = __self__ipred_wrt_theta_em;
__local["__self__ipred_wrt_theta_et50"] = __self__ipred_wrt_theta_et50;
__local["__self__ipred_wrt_eta_em"] = __self__ipred_wrt_eta_em;
__local["__self__ipred_wrt_eta_et50"] = __self__ipred_wrt_eta_et50;
__local["__self__ipred_wrt_eps"] = __self__ipred_wrt_eps;
__local["__self__y"] = __self__y;
__local["__self__y_wrt_theta_em"] = __self__y_wrt_theta_em;
__local["__self__y_wrt_theta_et50"] = __self__y_wrt_theta_et50;
__local["__self__y_wrt_eta_em"] = __self__y_wrt_eta_em;
__local["__self__y_wrt_eta_et50"] = __self__y_wrt_eta_et50;
__local["__self__y_wrt_eps"] = __self__y_wrt_eps;
// #endregion

// #region 将 reserved self attr 赋值至 __container
__container(0) = __self__ipred;
__container(1) = __self__y;
__container(2) = __self__ipred_wrt_theta_em;
__container(3) = __self__ipred_wrt_theta_et50;
__container(4) = __self__ipred_wrt_eta_em;
__container(5) = __self__ipred_wrt_eta_et50;
__container(6) = __self__ipred_wrt_eps;
__container(7) = __self__y_wrt_theta_em;
__container(8) = __self__y_wrt_theta_et50;
__container(9) = __self__y_wrt_eta_em;
__container(10) = __self__y_wrt_eta_et50;
__container(11) = __self__y_wrt_eps;
// #endregion
}
int main() {
    // pred(std::map<std::string, std::any>& self, double t, std::map<std::string, std::any>& __local, Eigen::VectorXd& __container)
    std::map<std::string, std::any> self;
//     __self__theta_em = std::any_cast<double>(self["theta_em"]);
// __self__theta_et50 = std::any_cast<double>(self["theta_et50"]);
// __self__eta_em = std::any_cast<double>(self["eta_em"]);
// __self__eta_et50 = std::any_cast<double>(self["eta_et50"]);
// __self__eps = std::any_cast<double>(self["eps"]);

// // 数据集中的协变量
// __self__mdv = std::any_cast<int>(self["mdv"]);
    self["theta_em"] = 9.5857E+01;
    self["theta_et50"] = 5.5869E-01;
    self["eta_em"] = -2.6389E-01;
    self["eta_et50"] = 8.2418E-02;
    self["eps"] = 0.01;
    self["wt"] = 50.1;

    Eigen::VectorXd container = Eigen::VectorXd::Zero(12);
    std::map<std::string, std::any> locals;

    std::vector<double> Time = { 0, 2, 4, 6, 8, 10, 12 };
    std::vector<double> HT = { 175.1, 176.1, 177.1, 178.1, 179.1, 180.1, 181.1 };

    for (int i = 0; i < Time.size(); i++) {
        double t = Time[i];
        double ht = HT[i];
        self["height"] = ht;
        pred(self, t, locals, container);
        std::cout << "t = " << t << std::endl;
        std::cout << "__self__ipred = " << container(0) << std::endl;
        std::cout << "__self__y = " << container(1) << std::endl;
        std::cout << "__self__ipred_wrt_eta_em = " << container(4) << std::endl;
        std::cout << "__self__ipred_wrt_eta_et50 = " << container(5) << std::endl;
        // std::cout << "ipred=" << std::any_cast<double>(locals["__self__ipred"]) << std::endl;
        std::cout << "==========" << std::endl;
    }

    
    return 0;
}