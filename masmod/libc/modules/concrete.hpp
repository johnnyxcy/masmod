/*
 * File: modules/concrete.hpp
 *
 * Author: Chongyi Xu <johnny.xcy1997@outlook.com>
 *
 * File Created: 12/07/2022 09:49 am
 *
 * Last Modified: 12/07/2022 02:05 pm
 *
 * Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
 *
 * Copyright (c) 2022 MaS Dev Team
 */
#pragma once

#include "masmod/libc/modules/interface.hpp"

namespace masmod::libc::modules {
/**
 * @brief () => IModule*
 */
typedef IModule* (*ModuleFactory)();

/**
 * @brief Module 对象的代理层，通过指针处理接口调用
 */
class ConcreteModule : public IModule {
   public:
    ConcreteModule() = default;

    /**
     * @brief 通过工厂函数构建 Module 指针
     *
     * @param module_factory 工厂函数，签名需要符合 () => IModule*
     */
    ConcreteModule(ModuleFactory module_factory) { this->impl_ = module_factory(); }

    virtual void pred(std::map<std::string, std::any>& context, double t,
                      std::map<std::string, std::any>& local_context, Eigen::VectorXd& container) override {
        this->impl_->pred(context, t, local_context, container);
    }

    /**
     * @brief 需要销毁 impl 指针
     */
    ~ConcreteModule() {
        delete this->impl_;
        this->impl_ = nullptr;
    }

   protected:
    IModule* impl_;
};
}  // namespace masmod::libc::modules
