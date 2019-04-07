#ifndef ONEFLOW_CORE_OPERATOR_BROADCAST_BINARY_OP_H_
#define ONEFLOW_CORE_OPERATOR_BROADCAST_BINARY_OP_H_

#include "oneflow/core/operator/operator.h"

namespace oneflow {

class BroadcastBinaryOp : public Operator {
 public:
  OF_DISALLOW_COPY_AND_MOVE(BroadcastBinaryOp);
  BroadcastBinaryOp() = default;
  virtual ~BroadcastBinaryOp() = default;

  void InitFromOpConf() override;
  bool IsAllOutputConst() const override { return GetValFromCustomizedConf<bool>("is_const"); }
  void InferBlobDescs(std::function<BlobDesc*(const std::string&)> GetBlobDesc4BnInOp,
                      const ParallelContext* parallel_ctx) const override;
  void InferBwBufBlobDescs(std::function<BlobDesc*(const std::string&)> GetBlobDesc4BnInOp,
                           const ParallelContext*) const override;

 private:
  bool IsInputBlobAllowedModelSplit(const std::string& ibn) const override { return true; }
  void GetSbpSignatureRules(std::vector<std::unique_ptr<const SbpSignatureRule>>*) const override;
};

}  // namespace oneflow

#endif  // ONEFLOW_CORE_OPERATOR_BROADCAST_BINARY_OP_H_
