import oneflow as flow
import numpy as np
import oneflow.core.operator.op_conf_pb2 as op_conf_util
from ops import *
import matplotlib.pyplot as plt
from datetime import datetime

def generator(z, trainable=True):
    n = z.static_shape[0]
    h0 = linear(z, 64 * 8 * 4 * 4, trainable=trainable)
    h0 = flow.reshape(h0, (n, 4, 4, 64 * 8))
    h0 = batch_norm(h0, trainable=trainable) # epsilon check fail
    h0 = relu(h0)

    h1 = deconv2d(h0, [n, 8, 8, 64 * 4], trainable=trainable)
    h1 = batch_norm(h1, trainable=trainable)
    h1 = relu(h1)

    h2 = deconv2d(h1, [n, 16, 16, 64 * 2], trainable=trainable)
    h2 = batch_norm(h2, trainable=trainable)
    h2 = relu(h2)

    h3 = deconv2d(h2, [n, 32, 32, 64], trainable=trainable)
    h3 = batch_norm(h3, trainable=trainable)
    h3 = relu(h3)

    h4 = deconv2d(h3, [n, 64, 64, 3], trainable=trainable)
    h4 = batch_norm(h4, trainable=trainable)
    out = tanh(h4)

    return out

def discriminator(image, trainable=True):
    h0 = conv2d(image, 64, trainable=trainable)
    h0 = lrelu(h0)

    h1 = conv2d(h0, 128, trainable=trainable)
    h1 = batch_norm(h1, trainable=trainable)
    h1 = lrelu(h1)

    h2 = conv2d(h1, 256, trainable=trainable)
    h2 = batch_norm(h2, trainable=trainable)
    h2 = lrelu(h2)

    h3 = conv2d(h2, 512, trainable=trainable)
    h3 = batch_norm(h3, trainable=trainable)
    h3 = lrelu(h3)

    h4 = flow.reshape(h3, (-1, 4 * 4 * 512))
    out = linear(h4, 1, trainable=trainable)

    return out


if __name__ == "__main__":

    bs = 8 # batch size

    @flow.function
    def train_generator(z=flow.input_blob_def((bs, 100)),
                        label1=flow.input_blob_def((bs, 1))):
        flow.config.train.primary_lr(0.0001)
        flow.config.train.model_update_conf(dict(naive_conf={}))
    
        g_out = generator(z, trainable=True)
        g_logits = discriminator(g_out, trainable=False)
        g_loss = flow.nn.sigmoid_cross_entropy_with_logits(label1, g_logits, name="Gloss_sigmoid_cross_entropy_with_logits")
        g_loss = g_loss * -1

        flow.losses.add_loss(g_loss)
        return g_loss, g_out
    
    @flow.function
    def train_discriminator(z=flow.input_blob_def((bs, 100)), 
                            label1=flow.input_blob_def((bs, 1)),
                            label0=flow.input_blob_def((bs, 1))):
        flow.config.train.primary_lr(0.0001)
        flow.config.train.model_update_conf(dict(naive_conf={}))

        g_out = generator(z, trainable=False)
        g_logits = discriminator(g_out, trainable=True)
        d_loss_fake = flow.nn.sigmoid_cross_entropy_with_logits(label0, g_logits, name="Dloss_fake_sigmoid_cross_entropy_with_logits")

        _, images = load_images()
        d_logits = discriminator(images, trainable=True)
        d_loss_real = flow.nn.sigmoid_cross_entropy_with_logits(label1, d_logits, name="Dloss_real_sigmoid_cross_entropy_with_logits")

        d_loss = d_loss_fake + d_loss_real
        flow.losses.add_loss(d_loss)
        return d_loss, d_loss_fake, d_loss_real

    flow.config.gpu_device_num(1)
    flow.config.default_data_type(flow.float32)
    check_point = flow.train.CheckPoint()
    check_point.init()

    for i in range(200):

        for j in range(1):
            z = np.random.randn(bs, 100).astype(np.float32)
            label1 = np.ones((bs, 1)).astype(np.float32)
            label0 = np.zeros((bs, 1)).astype(np.float32)
            d_loss, d_loss_fake, d_loss_real = train_discriminator(z, label1, label0).get()
        print("dloss:", d_loss.mean())
        # print("dloss_fake:", d_loss_fake.mean())
        # print("dloss_real:", d_loss_real.mean())

        for j in range(2):
            z = np.random.randn(bs, 100).astype(np.float32)
            label1 = np.ones((bs, 1)).astype(np.float32)
            g_loss, g_out = train_generator(z, label1).get()
        print("gloss:", g_loss.mean())

        
        if  (i + 1) % 10 == 0:
            print(i + 1,"th epoch:")
            # print("z:", z[0][:10])
            img = g_out[1] / 2 + 0.5
            plt.imsave("gout/test_{}.png".format(str(i+1)), img)
        
        # if (i + 1) % 10 == 0:
        #     check_point.save("./model_save-{}".format(str(datetime.now().strftime("%Y-%m-%d-%H:%M:%S")))+ str(i))

    
    

