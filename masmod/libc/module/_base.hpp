/*
 * File: module/_base.hpp
 *
 * Author: Chongyi Xu <johnny.xcy1997@outlook.com>
 *
 * File Created: 12/06/2022 05:35 pm
 *
 * Last Modified: 12/06/2022 05:46 pm
 *
 * Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
 *
 * Copyright (c) 2022 MaS Dev Team
 */
#include <Eigen/Dense>
#include <any>
#include <map>

class BaseModule {
   public:
    virtual ~BaseModule();
    virtual void pred(std::map<std::string, std::any>& self, double t, std::map<std::string, std::any>& __local,
                      Eigen::VectorXd& __container) = 0;
};

class Module {
   public:
    BaseModule* impl_;
};