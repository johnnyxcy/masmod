/*
 * File: modules/dylib.hpp
 *
 * Author: Chongyi Xu <johnny.xcy1997@outlook.com>
 *
 * File Created: 12/07/2022 09:23 am
 *
 * Last Modified: 12/07/2022 02:10 pm
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
#include "masmod/libc/modules/concrete.hpp"

namespace masmod::libc::modules {

/**
 * @brief 通过 dylib 构建的 Module 对象
 * @note dylib 必须要含有 __dylib_module_factory 函数
 * @attention DylibModule 不应该管理 dylib 的生命周期，应该交予上层处理 dylib 的 open 和 close
 */
class DylibModule : public ConcreteModule {
   public:
    DylibModule(void* dylib) : ConcreteModule((ModuleFactory)(__DYLIB_SYM(dylib, "__dylib_module_factory"))) {}
};

}  // namespace masmod::libc::modules
