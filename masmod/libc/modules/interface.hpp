/*
 * File: modules/interface.hpp
 *
 * Author: Chongyi Xu <johnny.xcy1997@outlook.com>
 *
 * File Created: 12/06/2022 05:35 pm
 *
 * Last Modified: 12/07/2022 01:32 pm
 *
 * Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
 *
 * Copyright (c) 2022 MaS Dev Team
 */
#pragma once

#include <Eigen/Dense>
#include <any>
#include <map>

#include "masmod/libc/dylib/dylib.hpp"

namespace masmod::libc::modules {

/**
 * @brief Module 的接口层，指定抽象方法
 * @note 接口层不应该被实例化
 */
class IModule {
   public:
    virtual ~IModule() = default;

    /**
     * @brief Module 的预测函数，处理模型的形式
     *
     * @param context 运行时所需要的上下文
     * @param t 预测点的时间戳
     * @param local_context 模型形式处理过程中获取的所有临时变量
     * @param container 结果容器
     * @details container(0) = ipred, container(1) = y
     * container(2 ... 2 + n_params) = dipred/dp, container(2 + n_params ... 2 + 2 * n_params) = dy/dp
     */
    virtual void pred(std::map<std::string, std::any>& context, double t,
                      std::map<std::string, std::any>& local_context, Eigen::VectorXd& container) = 0;
};

}  // namespace masmod::libc::modules
