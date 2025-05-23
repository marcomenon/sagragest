package pos.com.command.sdk;

import zj.com.customize.sdk.Other;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.ColorMatrix;
import android.graphics.ColorMatrixColorFilter;

import android.graphics.Paint;

public class PrintPicture {

	/**
	 * Print Bitmap Function
	 * This function prints a row as an image, making it less prone to errors during processing
	 * @param mBitmap
	 * @param nWidth
	 * @param nMode
	 * @return
	 */
    public static byte[] POS_PrintBMP(Bitmap mBitmap, int nWidth, int nMode) {

		int width = ((nWidth + 7) / 8) * 8;
		int height = mBitmap.getHeight() * width / mBitmap.getWidth();
		height = ((height + 7) / 8) * 8;

		Bitmap rszBitmap = mBitmap;
		if (mBitmap.getWidth() != width){
			rszBitmap = Other.resizeImage(mBitmap, width, height);
		}
	
		Bitmap grayBitmap = Other.toGrayscale(rszBitmap);

		//Bitmap grayBitmap = toGrayscale(rszBitmap);

		grayBitmap = convertGreyImgByFloyd(grayBitmap);
		
		byte[] dithered = Other.thresholdToBWPic(grayBitmap);

		byte[] data = Other.eachLinePixToCmd(dithered, width, nMode);

		return data;
	}

	public  static byte[] draw2PxPoint(Bitmap bmp) {

		int size = bmp.getWidth() * bmp.getHeight() / 8 + 1000;
		byte[] data = new byte[size];
		int k = 0;
		//Instructions for setting line spacing to 0
		data[k++] = 0x1B;
		data[k++] = 0x33;
		data[k++] = 0x00;
		// Print line by line
		for (int j = 0; j < bmp.getHeight() / 24f; j++) {
			//Instructions for printing images
			data[k++] = 0x1B;
			data[k++] = 0x2A;
			data[k++] = 33;
			data[k++] = (byte) (bmp.getWidth() % 256); //nL
			data[k++] = (byte) (bmp.getWidth() / 256); //nH
			//For each row, print column by column
			for (int i = 0; i < bmp.getWidth(); i++) {
				//Each column has 24 pixels, divided into 3 bytes for storage
				for (int m = 0; m < 3; m++) {
					//Each byte represents 8 pixels, 0 represents white, and 1 represents black
					for (int n = 0; n < 8; n++) {
						byte b = px2Byte(i, j * 24 + m * 8 + n, bmp);
						data[k] += data[k] + b;
					}
					k++;
				}
			}
			data[k++] = 10;
		}
		return data;
	}


	public static byte px2Byte(int x, int y, Bitmap bit) {
		if (x < bit.getWidth() && y < bit.getHeight()) {
			byte b;
			int pixel = bit.getPixel(x, y);
			int red = (pixel & 0x00ff0000) >> 16; // Take two digits higher
			int green = (pixel & 0x0000ff00) >> 8; // Take two places in the middle
			int blue = pixel & 0x000000ff; // Take down two digits
			int gray = RGB2Gray(red, green, blue);
			if (gray < 128) {
				b = 1;
			} else {
				b = 0;
			}
			return b;
		}
		return 0;
	}

	/**
	 * Conversion of image grayscale
	 */
	private static int RGB2Gray(int r, int g, int b) {
		int gray = (int) (0.29900 * r + 0.58700 * g + 0.11400 * b); //Gray scale conversion formula
		return gray;
	}


	/***
	 * Decolor the image and return a grayscale image
	 * @param bmpOriginal Incoming image
	 * @return Decolored image
	 */
	public static Bitmap toGrayscale(Bitmap bmpOriginal) {
		int width, height;
		height = bmpOriginal.getHeight();
		width = bmpOriginal.getWidth();


		Bitmap bmpGrayscale = Bitmap.createBitmap(width, height, Bitmap.Config.RGB_565);
		Canvas c = new Canvas(bmpGrayscale);
		Paint paint = new Paint();
		ColorMatrix cm = new ColorMatrix();
		cm.setSaturation(0);
		ColorMatrixColorFilter f = new ColorMatrixColorFilter(cm);
		paint.setColorFilter(f);
		c.drawBitmap(bmpOriginal, 0, 0, paint);
		return bmpGrayscale;
	}

   //Image Jitter Algorithm
	public static Bitmap convertGreyImgByFloyd(Bitmap img) {
		int width = img.getWidth();
		//Obtain the width of the bitmap
		int height = img.getHeight();
		//Obtain the height of the bitmap
		int[] pixels = new int[width * height];
		//Create a pixel array based on the size of the bitmap
		img.getPixels(pixels, 0, width, 0, 0, width, height);
		int[] gray = new int[height * width];
		for (int i = 0; i < height; i++) {
			for (int j = 0; j < width; j++) {
				int grey = pixels[width * i + j];
				int red = ((grey & 0x00FF0000) >> 16);
				gray[width * i + j] = red;
			}
		}
		int e = 0;
		for (int i = 0; i < height; i++) {
			for (int j = 0; j < width; j++) {
				int g = gray[width * i + j];
				if (g >= 128) {
					pixels[width * i + j] = 0xffffffff;
					e = g - 255;
				} else {
					pixels[width * i + j] = 0xff000000;
					e = g - 0;
				}
				if (j < width - 1 && i < height - 1) {

					gray[width * i + j + 1] += 3 * e / 8;

					gray[width * (i + 1) + j] += 3 * e / 8;

					gray[width * (i + 1) + j + 1] += e / 4;
				} else if (j == width - 1 && i < height - 1) {

					gray[width * (i + 1) + j] += 3 * e / 8;
				} else if (j < width - 1 && i == height - 1) {

					gray[width * (i) + j + 1] += e / 4;
				}
			}
		}
		Bitmap mBitmap = Bitmap.createBitmap(width, height, Bitmap.Config.RGB_565);
		mBitmap.setPixels(pixels, 0, width, 0, 0, width, height);
		return mBitmap;
	}


}
