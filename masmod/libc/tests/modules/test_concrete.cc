/*
 * File: modules/test_concrete.cc
 *
 * Author: Chongyi Xu <johnny.xcy1997@outlook.com>
 *
 * File Created: 12/06/2022 05:45 pm
 *
 * Last Modified: 12/07/2022 01:32 pm
 *
 * Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
 *
 * Copyright (c) 2022 MaS Dev Team
 */
#include <gtest/gtest.h>

#include "masmod/libc/modules/concrete.hpp"

namespace masmod::libc::modules {

class __TestConcreteModule : public IModule {
   public:
    void pred(std::map<std::string, std::any> &context, double t, std::map<std::string, std::any> &local_context,
              Eigen::VectorXd &container) override {
        container(0) = 0;
        container(1) = 1;
        container(2) = 2;
        container(3) = 3;
    };
};

inline IModule *test_module_factory() { return new __TestConcreteModule(); }

TEST(TestConcrete, test_construction) {
    auto mod = ConcreteModule(test_module_factory);
    std::map<std::string, std::any> context;
    std::map<std::string, std::any> locals;
    Eigen::VectorXd container(4);
    mod.pred(context, 0, locals, container);

    ASSERT_EQ(container.rows(), 4);
    ASSERT_EQ(container.cols(), 1);
}

}  // namespace masmod::libc::modules