package pos.com.cn.bluetooth.sdk;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.sql.Date;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Hashtable;
import java.util.List;
import java.util.Vector;


import com.google.zxing.BarcodeFormat;
import com.google.zxing.EncodeHintType;
import com.google.zxing.WriterException;
import com.google.zxing.common.BitMatrix;
import com.google.zxing.qrcode.QRCodeWriter;


import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import pos.com.cn.bluetooth.sdk.BluetoothService;
import pos.com.cn.bluetooth.sdk.DeviceListActivity;
import pos.com.cn.bluetooth.sdk.R;

import pos.com.command.sdk.Command;
import pos.com.command.sdk.PrintPicture;
import pos.com.command.sdk.PrinterCommand;
import zj.com.customize.sdk.Other;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlertDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.content.res.AssetManager;
import android.content.res.Resources;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.drawable.BitmapDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.provider.MediaStore;
import android.provider.MediaStore.MediaColumns;

import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.Window;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.RadioButton;
import android.widget.TextView;
import android.widget.Toast;

public class Main_Activity extends Activity implements OnClickListener {
    /******************************************************************************************************/

    protected String[] needPermissions = {
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.READ_EXTERNAL_STORAGE,
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO

    };


    private boolean isNeedCheck = true;


    // Debugging
    private static final String TAG = "Main_Activity";
    private static final boolean DEBUG = true;
    private boolean isReceive = false;
    /******************************************************************************************************/
    // Message types sent from the BluetoothService Handler
    public static final int MESSAGE_STATE_CHANGE = 1;
    public static final int MESSAGE_READ = 2;
    public static final int MESSAGE_WRITE = 3;
    public static final int MESSAGE_DEVICE_NAME = 4;
    public static final int MESSAGE_TOAST = 5;
    public static final int MESSAGE_CONNECTION_LOST = 6;
    public static final int MESSAGE_UNABLE_CONNECT = 7;
    public static final int MESSAGE_STOP_VIEW = 8;
    /*******************************************************************************************************/
    // Key names received from the BluetoothService Handler
    public static final String DEVICE_NAME = "device_name";
    public static final String TOAST = "toast";

    // Intent request codes
    private static final int REQUEST_CONNECT_DEVICE = 1;
    private static final int REQUEST_ENABLE_BT = 2;
    private static final int REQUEST_CHOSE_BMP = 3;
    private static final int REQUEST_CAMER = 4;

    //QRcode
    private static final int QR_WIDTH = 350;
    private static final int QR_HEIGHT = 350;
    /*******************************************************************************************************/
    private static final String code = "GBK";

    /*********************************************************************************/
    private TextView mTitle;
    EditText editText;
    ImageView imageViewPicture;
    private static boolean is58mm = true;
    private RadioButton width_58mm, width_80;

    private CheckBox hexBox;
    private Button sendButton = null;
    private Button testButton = null;
    private Button testButton1 = null;
    private Button printbmpButton = null;
    private Button btnScanButton = null;
    private Button btnClose = null;
    private Button btn_BMP = null;
    private Button btn_ChoseCommand = null;
    private Button btn_prtsma = null;
    private Button btn_prttableButton = null;
    private Button btn_prtcodeButton = null;
    private Button btn_scqrcode = null;
    private Button btn_camer = null;

    /******************************************************************************************************/
    // Name of the connected device
    private String mConnectedDeviceName = null;
    // Local Bluetooth adapter
    private BluetoothAdapter mBluetoothAdapter = null;
    // Member object for the services
    private BluetoothService mService = null;

    final String[] itemsen = {"Print Init", "Print and Paper", "Standard ASCII font", "Compressed ASCII font", "Normal size",
            "Double high", "Double wide", "Double high power wide", "Twice as high power wide", "Three times the high-powered wide", "Off emphasized mode", "Choose bold mode", "Cancel inverted Print", "Invert selection Print", "Cancel black and white reverse display", "Choose black and white reverse display",
            "Cancel rotated clockwise 90 °", "Select the clockwise rotation of 90 °", "Feed paper Cut", "Beep", "Standard CashBox",
            "Open CashBox", "Char Mode", "code Mode", "Print SelfTest", "DisEnable Button", "Enable Button",
            "Set Underline", "Cancel Underline", "Hex Mode"};
    final byte[][] byteCommands = {
            {0x1b, 0x40, 0x0a},
            {0x0a},
            {0x1b, 0x4d, 0x00},
            {0x1b, 0x4d, 0x01},
            {0x1d, 0x21, 0x00},
            {0x1d, 0x21, 0x11},
            {0x1B, 0x21, 0x10},
            {0x1B, 0x21, 0x20},
            {0x1d, 0x21, 0x22},
            {0x1d, 0x21, 0x33},
            {0x1b, 0x45, 0x00},
            {0x1b, 0x45, 0x01},
            {0x1b, 0x7b, 0x00},
            {0x1b, 0x7b, 0x01},
            {0x1d, 0x42, 0x00},
            {0x1d, 0x42, 0x01},
            {0x1b, 0x56, 0x00},
            {0x1b, 0x56, 0x01},
            {0x0a, 0x1d, 0x56, 0x42, 0x01, 0x0a},
            {0x1b, 0x42, 0x03, 0x03},
            {0x1b, 0x70, 0x00, 0x50, 0x50},
            {0x10, 0x14, 0x00, 0x05, 0x05},
            {0x1c, 0x2e},
            {0x1c, 0x26},
            {0x1f, 0x11, 0x04},
            {0x1b, 0x63, 0x35, 0x01},
            {0x1b, 0x63, 0x35, 0x00},
            {0x1b, 0x2d, 0x02, 0x1c, 0x2d, 0x02},
            {0x1b, 0x2d, 0x00, 0x1c, 0x2d, 0x00},
            {0x1f, 0x11, 0x03},
    };

    final String[] codebar = {"UPC_A", "UPC_E", "JAN13(EAN13)", "JAN8(EAN8)",
            "CODE39", "ITF", "CODABAR", "CODE93", "CODE128", "QR Code"};
    final byte[][] byteCodebar = {
            {0x1b, 0x40},
            {0x1b, 0x40},
            {0x1b, 0x40},
            {0x1b, 0x40},
            {0x1b, 0x40},
            {0x1b, 0x40},
            {0x1b, 0x40},
            {0x1b, 0x40},
            {0x1b, 0x40},
            {0x1b, 0x40},
    };

    /******************************************************************************************************/

    //private blueRe mReceiver;
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (DEBUG)
            Log.e(TAG, "+++ ON CREATE +++");



        // Set up the window layout
 //       requestWindowFeature(Window.FEATURE_CUSTOM_TITLE);
        //    requestWindowFeature(Window.FEATURE_NO_TITLE);
        setContentView(R.layout.main);
//        getWindow().setFeatureInt(Window.FEATURE_CUSTOM_TITLE,
//                R.layout.custom_title);

        // Set up the custom title
        mTitle = (TextView) findViewById(R.id.title_left_text);
        mTitle.setText(R.string.app_title);
        mTitle = (TextView) findViewById(R.id.title_right_text);

        // Get local Bluetooth adapter
        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        // If the adapter is null, then Bluetooth is not supported
        if (mBluetoothAdapter == null) {
            Toast.makeText(this, "Bluetooth is not available",
                    Toast.LENGTH_LONG).show();
            finish();
        }

    }





    @Override
    public void onStart() {
        super.onStart();

        // If Bluetooth is not on, request that it be enabled.
        // setupChat() will then be called during onActivityResult
        if (!mBluetoothAdapter.isEnabled()) {
            Intent enableIntent = new Intent(
                    BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableIntent, REQUEST_ENABLE_BT);
            // Otherwise, setup the session
        } else {
            if (mService == null)
                KeyListenerInit();
        }
    }


    private void checkPermissions(String... permissions) {
        List<String> needRequestPermissonList = findDeniedPermissions(permissions);
        if (null != needRequestPermissonList && needRequestPermissonList.size() > 0) {
            ActivityCompat.requestPermissions(Main_Activity.this, needRequestPermissonList.toArray(
                    new String[needRequestPermissonList.size()]),
                    1);
        }
    }


    private List<String> findDeniedPermissions(String[] permissions) {
        List<String> needRequestPermissonList = new ArrayList<String>();
        for (String perm : permissions) {
            if (ContextCompat.checkSelfPermission(Main_Activity.this, perm) != PackageManager.PERMISSION_GRANTED) {
                needRequestPermissonList.add(perm);
            } else {
                if (ActivityCompat.shouldShowRequestPermissionRationale(Main_Activity.this, perm)) {
                    needRequestPermissonList.add(perm);
                }
            }
        }
        return needRequestPermissonList;
    }


    private boolean verifyPermissions(int[] grantResults) {
        for (int result : grantResults) {
            if (result != PackageManager.PERMISSION_GRANTED) {
                return false;
            }
        }
        return true;
    }

    @SuppressLint({"Override", "NewApi"})
    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] paramArrayOfInt) {
        if (requestCode == 1) {
            if (!verifyPermissions(paramArrayOfInt)) {
                //showMissingPermissionDialog();
                isNeedCheck = false;
            }

        }

    }

    @Override
    public synchronized void onResume() {
        super.onResume();
        if (isNeedCheck) {
            checkPermissions(needPermissions);
        }
        if (mService != null) {

            if (mService.getState() == BluetoothService.STATE_NONE) {
                // Start the Bluetooth services
                mService.start();
            }
        }
    }

    @Override
    public synchronized void onPause() {
        super.onPause();
        if (DEBUG)
            Log.e(TAG, "- ON PAUSE -");
    }

    @Override
    public void onStop() {
        super.onStop();
        if (DEBUG)
            Log.e(TAG, "-- ON STOP --");
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        // Stop the Bluetooth services
        if (mService != null)
            mService.stop();
        if (DEBUG)
            Log.e(TAG, "--- ON DESTROY ---");


    }

    /*****************************************************************************************************/
    private void KeyListenerInit() {

        editText = (EditText) findViewById(R.id.edit_text_out);

        sendButton = (Button) findViewById(R.id.Send_Button);
        sendButton.setOnClickListener(this);

        testButton = (Button) findViewById(R.id.btn_test);
        testButton.setOnClickListener(this);

        testButton1 = findViewById(R.id.btn_test1);
        testButton1.setOnClickListener(this);

        printbmpButton = (Button) findViewById(R.id.btn_printpicture);
        printbmpButton.setOnClickListener(this);

        btnScanButton = (Button) findViewById(R.id.button_scan);
        btnScanButton.setOnClickListener(this);

        hexBox = (CheckBox) findViewById(R.id.checkBoxHEX);
        hexBox.setOnClickListener(this);

        width_58mm = (RadioButton) findViewById(R.id.width_58mm);
        width_58mm.setOnClickListener(this);

        width_80 = (RadioButton) findViewById(R.id.width_80mm);
        width_80.setOnClickListener(this);

        imageViewPicture = (ImageView) findViewById(R.id.imageViewPictureUSB);
        imageViewPicture.setOnClickListener(this);

        btnClose = (Button) findViewById(R.id.btn_close);
        btnClose.setOnClickListener(this);

        btn_BMP = (Button) findViewById(R.id.btn_prtbmp);
        btn_BMP.setOnClickListener(this);

        btn_ChoseCommand = (Button) findViewById(R.id.btn_prtcommand);
        btn_ChoseCommand.setOnClickListener(this);

        btn_prtsma = (Button) findViewById(R.id.btn_prtsma);
        btn_prtsma.setOnClickListener(this);

        btn_prttableButton = (Button) findViewById(R.id.btn_prttable);
        btn_prttableButton.setOnClickListener(this);

        btn_prtcodeButton = (Button) findViewById(R.id.btn_prtbarcode);
        btn_prtcodeButton.setOnClickListener(this);

        btn_camer = (Button) findViewById(R.id.btn_dyca);
        btn_camer.setOnClickListener(this);

        btn_scqrcode = (Button) findViewById(R.id.btn_scqr);
        btn_scqrcode.setOnClickListener(this);

        Bitmap bm = getImageFromAssetsFile("printer.png");
        if (null != bm) {
            imageViewPicture.setImageBitmap(bm);
        }

        editText.setEnabled(false);
        imageViewPicture.setEnabled(false);
        width_58mm.setEnabled(false);
        width_80.setEnabled(false);

        hexBox.setEnabled(false);
        sendButton.setEnabled(false);
        testButton.setEnabled(false);
        testButton1.setEnabled(false);
        printbmpButton.setEnabled(false);
        btnClose.setEnabled(false);
        btn_BMP.setEnabled(false);
        btn_ChoseCommand.setEnabled(false);
        btn_prtcodeButton.setEnabled(false);
        btn_prtsma.setEnabled(false);
        btn_prttableButton.setEnabled(false);
        btn_camer.setEnabled(false);
        btn_scqrcode.setEnabled(false);


        mService = new BluetoothService(this, mHandler);
    }

    @Override
    public void onClick(View v) {
        // TODO Auto-generated method stub
        switch (v.getId()) {
            case R.id.button_scan: {


                if (!mBluetoothAdapter.isEnabled()) {
                    Intent enableIntent = new Intent(
                            BluetoothAdapter.ACTION_REQUEST_ENABLE);
                    startActivityForResult(enableIntent, REQUEST_ENABLE_BT);

                    return;
                } else {
                    if (mService == null)
                        KeyListenerInit();
                }


                Intent serverIntent = new Intent(Main_Activity.this, DeviceListActivity.class);
                startActivityForResult(serverIntent, REQUEST_CONNECT_DEVICE);

                break;
            }
            case R.id.btn_close: {
                stop();
                break;
            }
            case R.id.btn_test: {
                //BluetoothPrintTest1(true);
                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        Print_Test();
                    }
                }).start();

                ;
                break;
            }


            case R.id.Send_Button: {
                if (hexBox.isChecked()) {
                    String str = editText.getText().toString().trim();
                    if (str.length() > 0) {
                        str = Other.RemoveChar(str, ' ').toString();
                        if (str.length() <= 0)
                            return;
                        if ((str.length() % 2) != 0) {
                            Toast.makeText(getApplicationContext(), getString(R.string.msg_state),
                                    Toast.LENGTH_SHORT).show();
                            return;
                        }
                        byte[] buf = Other.HexStringToBytes(str);
                        SendDataByte(buf);
                    } else {
                        Toast.makeText(Main_Activity.this, getText(R.string.empty), Toast.LENGTH_SHORT).show();
                    }
                } else {
                    final String msg = editText.getText().toString();
                    if (msg.length() > 0) {
                        new Thread(new Runnable() {
                            @Override
                            public void run() {

                                    SendDataByte(Command.GS_W1);
                                    //SendDataByte(PrinterCommand.POS_Print_Text(msg, CP1252, 16, 0, 0, 0));
                                    SendDataString(msg);
                                    SendDataByte(Command.LF);
                                }

                        }).start();

                        //SendDataByte(Command.ESC_Init);
                    } else {
                        Toast.makeText(Main_Activity.this, getText(R.string.empty), Toast.LENGTH_SHORT).show();
                    }
                }
                break;
            }
            case R.id.width_58mm: {

            }
//            case R.id.width_80mm: {
//                is58mm = v == width_58mm;
//                width_58mm.setChecked(is58mm);
//                width_80.setChecked(!is58mm);
//                width_110mm.setChecked(false);
//                break;
//            }

            case R.id.width_80mm: {
                is58mm = v == width_58mm;
                width_58mm.setChecked(is58mm);
                width_80.setChecked(!is58mm);

                break;
            }


            case R.id.btn_printpicture: {
                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        GraphicalPrint();
                    }
                }).start();

                break;
            }
            case R.id.imageViewPictureUSB: {
                Intent loadpicture = new Intent(
                        Intent.ACTION_PICK,
                        MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
                startActivityForResult(loadpicture, REQUEST_CHOSE_BMP);
                break;
            }
            case R.id.btn_prtbmp: {
                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        Print_BMP();
                    }
                }).start();

                break;
            }
            case R.id.btn_prtcommand: {
                CommandTest();
                break;
            }
            case R.id.btn_prtsma: {
                SendDataByte(Command.ESC_Init);
                SendDataByte(Command.LF);
                Print_Ex();


                break;
            }
            case R.id.btn_prttable: {
                SendDataByte(Command.ESC_Init);
                SendDataByte(Command.LF);
                PrintTable();
                break;
            }
            case R.id.btn_prtbarcode: {
                printBarCode();
                break;
            }
            case R.id.btn_scqr: {
                createImage();
                break;
            }
            case R.id.btn_dyca: {
                dispatchTakePictureIntent(REQUEST_CAMER);
                break;
            }
            default:
                break;
        }
    }


    private void stop() {
        mService.stop();
        editText.setEnabled(false);
        imageViewPicture.setEnabled(false);
        width_58mm.setEnabled(false);
        width_80.setEnabled(false);
        hexBox.setEnabled(false);
        sendButton.setEnabled(false);
        testButton.setEnabled(false);
        testButton1.setEnabled(false);
        printbmpButton.setEnabled(false);
        btnClose.setEnabled(false);
        btn_BMP.setEnabled(false);
        btn_ChoseCommand.setEnabled(false);
        btn_prtcodeButton.setEnabled(false);
        btn_prtsma.setEnabled(false);
        btn_prttableButton.setEnabled(false);
        btn_camer.setEnabled(false);
        btn_scqrcode.setEnabled(false);
        btnScanButton.setEnabled(true);

        btnScanButton.setText(getText(R.string.connect));
    }

    /*****************************************************************************************************/
    /*
     * SendDataString
     */
    private void SendDataString(String data) {

        if (mService.getState() != BluetoothService.STATE_CONNECTED) {
            Toast.makeText(this, R.string.not_connected, Toast.LENGTH_SHORT)
                    .show();
            return;
        }
        if (data.length() > 0) {
            try {
                mService.write(data.getBytes(code));
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            }
        }
    }

    private void SendDataStringEncode(String data, String encode) {

        if (mService.getState() != BluetoothService.STATE_CONNECTED) {
            Toast.makeText(this, R.string.not_connected, Toast.LENGTH_SHORT)
                    .show();
            return;
        }
        if (data.length() > 0) {
            try {
                mService.write(data.getBytes(encode));
                mService.write(data.getBytes(data));

            } catch (UnsupportedEncodingException e) {

                e.printStackTrace();
            }
        }
    }

    /*
     *SendDataByte
     */
    private void SendDataByte(byte[] data) {

        if (mService.getState() != BluetoothService.STATE_CONNECTED) {
            if(Looper.myLooper()==null)
            Looper.prepare();
            Toast.makeText(this, R.string.not_connected, Toast.LENGTH_SHORT)
                    .show();
            Looper.loop();
            return;
        }
        mService.write(data);
    }

    /****************************************************************************************************/
    @SuppressLint("HandlerLeak")
    private final Handler mHandler = new Handler() {
        @Override
        public void handleMessage(Message msg) {


            switch (msg.what) {
                case MESSAGE_STATE_CHANGE:
                    if (DEBUG)
                        Log.i(TAG, "MESSAGE_STATE_CHANGE: " + msg.arg1);
                    switch (msg.arg1) {
                        case BluetoothService.STATE_CONNECTED:
                            mTitle.setText(R.string.title_connected_to);
                            mTitle.append(mConnectedDeviceName);
                            btnScanButton.setText(getText(R.string.Connecting));
                            Toast.makeText(getApplicationContext(),
                                    R.string.Connecting, Toast.LENGTH_SHORT)
                                    .show();
                            Print_Test();
                            btnScanButton.setEnabled(false);
                            editText.setEnabled(true);
                            imageViewPicture.setEnabled(true);
                            width_58mm.setEnabled(true);
                            width_80.setEnabled(true);

                            hexBox.setEnabled(true);
                            sendButton.setEnabled(true);
                            testButton.setEnabled(true);
                            testButton1.setEnabled(true);
                            printbmpButton.setEnabled(true);
                            btnClose.setEnabled(true);
                            btn_BMP.setEnabled(true);
                            btn_ChoseCommand.setEnabled(true);
                            btn_prtcodeButton.setEnabled(true);
                            btn_prtsma.setEnabled(true);
                            btn_prttableButton.setEnabled(true);
                            btn_camer.setEnabled(true);
                            btn_scqrcode.setEnabled(true);



                            break;
                        case BluetoothService.STATE_CONNECTING:
                            mTitle.setText(R.string.title_connecting);
                            break;
                        case BluetoothService.STATE_LISTEN:
                        case BluetoothService.STATE_NONE:
                            mTitle.setText(R.string.title_not_connected);
                            break;
                    }
                    break;
                case MESSAGE_WRITE:

                    break;
                case MESSAGE_READ:


                    break;
                case MESSAGE_DEVICE_NAME:
                    // save the connected device's name
                    mConnectedDeviceName = msg.getData().getString(DEVICE_NAME);

                    break;
                case MESSAGE_TOAST:
                    Toast.makeText(getApplicationContext(),
                            msg.getData().getString(TOAST), Toast.LENGTH_SHORT)
                            .show();
                    break;
                case MESSAGE_CONNECTION_LOST:
                    Toast.makeText(getApplicationContext(), "Device connection was lost",
                            Toast.LENGTH_SHORT).show();
                    editText.setEnabled(false);
                    imageViewPicture.setEnabled(false);
                    width_58mm.setEnabled(false);
                    width_80.setEnabled(false);
                    hexBox.setEnabled(false);
                    sendButton.setEnabled(false);
                    testButton.setEnabled(false);
                    testButton1.setEnabled(false);
                    printbmpButton.setEnabled(false);
                    btnClose.setEnabled(false);
                    btn_BMP.setEnabled(false);
                    btn_ChoseCommand.setEnabled(false);
                    btn_prtcodeButton.setEnabled(false);
                    btn_prtsma.setEnabled(false);
                    btn_prttableButton.setEnabled(false);
                    btn_camer.setEnabled(false);
                    btn_scqrcode.setEnabled(false);

                    break;
                case MESSAGE_UNABLE_CONNECT:
                    Toast.makeText(getApplicationContext(), "Unable to connect device",
                            Toast.LENGTH_SHORT).show();
                    break;
                case MESSAGE_STOP_VIEW:
                    stop();
                    break;
            }
        }
    };

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (DEBUG)
            Log.d(TAG, "onActivityResult " + resultCode);
        switch (requestCode) {
            case REQUEST_CONNECT_DEVICE: {
                // When DeviceListActivity returns with a device to connect
                if (resultCode == Activity.RESULT_OK) {
                    // Get the device MAC address
                    //BluetoothDevice device = data.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                    String address = data.getExtras().getString(
                            DeviceListActivity.EXTRA_DEVICE_ADDRESS);
                    // Get the BLuetoothDevice object
                    if (BluetoothAdapter.checkBluetoothAddress(address)) {
                        BluetoothDevice device = mBluetoothAdapter
                                .getRemoteDevice(address);
                        // Attempt to connect to the device
                        mService.connect(device);
                        try {

                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                }
                break;
            }
            case REQUEST_ENABLE_BT: {
                // When the request to enable Bluetooth returns
                if (resultCode == Activity.RESULT_OK) {
                    // Bluetooth is now enabled, so set up a session
                    KeyListenerInit();
                } else {
                    // User did not enable Bluetooth or an error occured
                    Log.d(TAG, "BT not enabled");
                    Toast.makeText(this, R.string.bt_not_enabled_leaving,
                            Toast.LENGTH_SHORT).show();
                    finish();
                }
                break;
            }
            case REQUEST_CHOSE_BMP: {
                if (resultCode == Activity.RESULT_OK) {
                    Uri selectedImage = data.getData();
                    String[] filePathColumn = {MediaColumns.DATA};

                    Cursor cursor = getContentResolver().query(selectedImage,
                            filePathColumn, null, null, null);
                    cursor.moveToFirst();

                    int columnIndex = cursor.getColumnIndex(filePathColumn[0]);
                    String picturePath = cursor.getString(columnIndex);
                    cursor.close();

                    BitmapFactory.Options opts = new BitmapFactory.Options();
                    opts.inJustDecodeBounds = true;
                    BitmapFactory.decodeFile(picturePath, opts);
                    opts.inJustDecodeBounds = false;
                    if (opts.outWidth > 1200) {
                        opts.inSampleSize = opts.outWidth / 1200;
                    }
                    Bitmap bitmap = BitmapFactory.decodeFile(picturePath, opts);
                    if (null != bitmap) {
                        imageViewPicture.setImageBitmap(bitmap);
                    }
                } else {
                    Toast.makeText(this, getString(R.string.msg_statev1), Toast.LENGTH_SHORT).show();
                }
                break;
            }
            case REQUEST_CAMER: {
                if (resultCode == Activity.RESULT_OK) {
                    handleSmallCameraPhoto(data);
                } else {
                    Toast.makeText(this, getText(R.string.camer), Toast.LENGTH_SHORT).show();
                }
                break;
            }
        }
    }

/****************************************************************************************************/
    /**
     * Print test page after successful connection
     */
    private void Print_Test() {
        String lang = getString(R.string.strLang);
        String msg = "Congratulations!\n\n";
        String data = "You have sucessfully created communications between your device and our bluetooth printer.\n"
                    + "  the company is a high-tech enterprise which specializes" +
                    " in R&D,manufacturing,marketing of thermal printers and barcode scanners.\n\n";
        SendDataByte(PrinterCommand.POS_Print_Text(msg, code, 0, 1, 1, 0));
        SendDataByte(PrinterCommand.POS_Print_Text(data, code, 0, 0, 0, 0));
        SendDataByte(PrinterCommand.POS_Set_Cut(1));
        SendDataByte(PrinterCommand.POS_Set_PrtInit());
        SendDataByte(new byte[]{0x1B, 0x59, 0x5A, 0x01});

    }

    /*
     * print a picture
     */
    private void Print_BMP() {
        Bitmap mBitmap = ((BitmapDrawable) imageViewPicture.getDrawable()).getBitmap();
        int nMode = 0;
        int nPaperWidth = 384;
        if (width_58mm.isChecked()) {
            nPaperWidth = 384;
        } else if (width_80.isChecked()) {
            nPaperWidth = 576;
        }
        if (mBitmap != null) {
            /**
             * Parameters:
             * mBitmap  Picture to print
             * nWidth   Print Width（58 and 80）
             * nMode    print mode
             * Returns: byte[]
             */
            byte[] data = PrintPicture.POS_PrintBMP(mBitmap, nPaperWidth, nMode);
            SendDataByte(Command.GS_W1);
            SendDataByte(Command.ESC_Init);
            SendDataByte(Command.LF);
            SendDataByte(data);
            SendDataByte(PrinterCommand.POS_Set_PrtAndFeedPaper(30));
            SendDataByte(PrinterCommand.POS_Set_Cut(1));
            SendDataByte(PrinterCommand.POS_Set_PrtInit());
        }
    }

    public  byte[] ByteTo_byte(Vector<Byte> vector) {
        int len = vector.size();
        byte[] data = new byte[len];

        for(int i = 0; i < len; ++i) {
            data[i] = ((Byte)vector.get(i)).byteValue();
        }

        return data;
    }

    /**
     * Print Custom Tables
     */
    @SuppressLint("SimpleDateFormat")
    private void PrintTable() {
        SimpleDateFormat formatter = new SimpleDateFormat("yyyy/MM/dd/ HH:mm:ss ");
        Date curDate = new Date(System.currentTimeMillis());
        String str = formatter.format(curDate);
        String date = str + "\n\n\n\n\n\n";
        if (is58mm) {

            Command.ESC_Align[2] = 0x02;
            byte[][] allbuf;
            try {
                    allbuf = new byte[][]{

                            Command.ESC_Init, Command.ESC_Three,
                            String.format("┏━━┳━━━┳━━┳━━━━┓\n").getBytes(code),
                            String.format("┃XXXX┃%-6s┃XXXX┃%-8s┃\n", "XXXX", "XXXX").getBytes(code),
                            String.format("┣━━╋━━━╋━━╋━━━━┫\n").getBytes(code),
                            String.format("┃XXXX┃%2d/%-3d┃XXXX┃%-8d┃\n", 1, 222, 555).getBytes(code),
                            String.format("┣━━┻┳━━┻━━┻━━━━┫\n").getBytes(code),
                            String.format("┃XXXXXX┃%-18s┃\n", "【XX】XXXX/XXXXXX").getBytes(code),
                            String.format("┣━━━╋━━┳━━┳━━━━┫\n").getBytes(code),
                            String.format("┃XXXXXX┃%-2s┃XXXX┃%-8s┃\n", "XXXX", "XXXX").getBytes(code),
                            String.format("┗━━━┻━━┻━━┻━━━━┛\n").getBytes(code),
                            Command.ESC_Align, "\n".getBytes(code)
                    };
                    byte[] buf = Other.byteArraysToBytes(allbuf);
                    SendDataByte(buf);
                    SendDataString(date);
                    SendDataByte(Command.GS_V_m_n);
                } catch (UnsupportedEncodingException e) {

                    e.printStackTrace();
                }

        }
    }

    /**
     * Print Custom Tickets
     */
    @SuppressLint("SimpleDateFormat")
    private void Print_Ex() {

        String lang = getString(R.string.strLang);

            SimpleDateFormat formatter = new SimpleDateFormat("yyyy/MM/dd/ HH:mm:ss ");
            Date curDate = new Date(System.currentTimeMillis());
            String str = formatter.format(curDate);
            String date = str + "\n\n\n\n\n\n";
            if (is58mm) {

                try {
                    byte[] qrcode = PrinterCommand.getBarCommand("Electronic Thermal Receipt Printer!", 0, 3, 6);//
                    Command.ESC_Align[2] = 0x01;
                    SendDataByte(Command.ESC_Align);
                    SendDataByte(qrcode);

                    SendDataByte(Command.ESC_Align);
                    Command.GS_ExclamationMark[2] = 0x11;
                    SendDataByte(Command.GS_ExclamationMark);
                    SendDataByte("Itos Technology, S.L.\n".getBytes(code));
                    Command.ESC_Align[2] = 0x00;
                    SendDataByte(Command.ESC_Align);
                    Command.GS_ExclamationMark[2] = 0x00;
                    SendDataByte(Command.GS_ExclamationMark);

                    Command.ESC_Align[2] = 0x01;
                    SendDataByte(Command.ESC_Align);
                    Command.GS_ExclamationMark[2] = 0x11;
                    SendDataByte(Command.GS_ExclamationMark);
                    SendDataByte("Welcome again!\n".getBytes(code));
                    Command.ESC_Align[2] = 0x00;
                    SendDataByte(Command.ESC_Align);
                    Command.GS_ExclamationMark[2] = 0x00;
                    SendDataByte(Command.GS_ExclamationMark);

                    SendDataByte("(The above information is for testing template, if agree, is purely coincidental!)\n".getBytes(code));
                    Command.ESC_Align[2] = 0x02;
                    SendDataByte(Command.ESC_Align);
                    SendDataString(date);
                    SendDataByte(PrinterCommand.POS_Set_PrtAndFeedPaper(48));
                    SendDataByte(Command.GS_V_m_n);


                    new Handler().postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            SendDataByte(new byte[]{0x1B, 0x59, 0x5A, 0x01});
                        }
                    }, 5000);
                } catch (UnsupportedEncodingException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
            } else {
                try {
                    byte[] qrcode = PrinterCommand.getBarCommand("Electronic Thermal Receipt Printer!", 0, 3, 8);
                    Command.ESC_Align[2] = 0x01;
                    SendDataByte(Command.ESC_Align);
                    SendDataByte(qrcode);

                    Command.ESC_Align[2] = 0x01;
                    SendDataByte(Command.ESC_Align);
                    Command.GS_ExclamationMark[2] = 0x11;
                    SendDataByte(Command.GS_ExclamationMark);
                    SendDataByte("Itos Technology, S.L.\n".getBytes(code));
                    Command.ESC_Align[2] = 0x00;
                    SendDataByte(Command.ESC_Align);
                    Command.GS_ExclamationMark[2] = 0x00;
                    SendDataByte(Command.GS_ExclamationMark);

                    Command.ESC_Align[2] = 0x01;
                    SendDataByte(Command.ESC_Align);
                    Command.GS_ExclamationMark[2] = 0x11;
                    SendDataByte(Command.GS_ExclamationMark);
                    SendDataByte("Welcome again!\n".getBytes(code));
                    Command.ESC_Align[2] = 0x00;
                    SendDataByte(Command.ESC_Align);
                    Command.GS_ExclamationMark[2] = 0x00;
                    SendDataByte(Command.GS_ExclamationMark);
                    SendDataByte("(The above information is for testing template, if agree, is purely coincidental!)\n".getBytes(code));
                    Command.ESC_Align[2] = 0x02;
                    SendDataByte(Command.ESC_Align);
                    SendDataString(date);
                    SendDataByte(PrinterCommand.POS_Set_PrtAndFeedPaper(48));
                    SendDataByte(Command.GS_V_m_n);


                    new Handler().postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            SendDataByte(new byte[]{0x1B, 0x59, 0x5A, 0x01});
                        }
                    }, 1500);
                } catch (UnsupportedEncodingException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
            }

    }

    /**
     * Print barcode and QR code
     */
    private void printBarCode() {

        new AlertDialog.Builder(Main_Activity.this).setTitle(getText(R.string.btn_prtcode))
                .setItems(codebar, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        SendDataByte(byteCodebar[which]);
                        String str = editText.getText().toString();
                        if (which == 0) {
                            if (str.length() == 11 || str.length() == 12) {
                                byte[] code = PrinterCommand.getCodeBarCommand(str, 65, 3, 168, 0, 2);
                                SendDataByte(new byte[]{0x1b, 0x61, 0x00});
                                SendDataString("UPC_A\n");
                                SendDataByte(code);
                            } else {
                                Toast.makeText(Main_Activity.this, getText(R.string.msg_error), Toast.LENGTH_SHORT).show();
                                return;
                            }
                        } else if (which == 1) {
                            if (str.length() == 6 || str.length() == 7) {
                                byte[] code = PrinterCommand.getCodeBarCommand(str, 66, 3, 168, 0, 2);
                                SendDataByte(new byte[]{0x1b, 0x61, 0x00});
                                SendDataString("UPC_E\n");
                                SendDataByte(code);
                            } else {
                                Toast.makeText(Main_Activity.this, getText(R.string.msg_error), Toast.LENGTH_SHORT).show();
                                return;
                            }
                        } else if (which == 2) {
                            if (str.length() == 12 || str.length() == 13) {
                                byte[] code = PrinterCommand.getCodeBarCommand(str, 67, 3, 168, 0, 2);
                                SendDataByte(new byte[]{0x1b, 0x61, 0x00});
                                SendDataString("JAN13(EAN13)\n");
                                SendDataByte(code);
                            } else {
                                Toast.makeText(Main_Activity.this, getText(R.string.msg_error), Toast.LENGTH_SHORT).show();
                                return;
                            }
                        } else if (which == 3) {
                            if (str.length() > 0) {
                                byte[] code = PrinterCommand.getCodeBarCommand(str, 68, 3, 168, 0, 2);
                                SendDataByte(new byte[]{0x1b, 0x61, 0x00});
                                SendDataString("JAN8(EAN8)\n");
                                SendDataByte(code);
                            } else {
                                Toast.makeText(Main_Activity.this, getText(R.string.msg_error), Toast.LENGTH_SHORT).show();
                                return;
                            }
                        } else if (which == 4) {
                            if (str.length() == 0) {
                                Toast.makeText(Main_Activity.this, getText(R.string.msg_error), Toast.LENGTH_SHORT).show();
                                return;
                            } else {
                                byte[] code = PrinterCommand.getCodeBarCommand(str, 69, 3, 168, 1, 2);
                                SendDataString("CODE39\n");
                                SendDataByte(new byte[]{0x1b, 0x61, 0x00});
                                SendDataByte(code);
                            }
                        } else if (which == 5) {
                            if (str.length() == 0) {
                                Toast.makeText(Main_Activity.this, getText(R.string.msg_error), Toast.LENGTH_SHORT).show();
                                return;
                            } else {
                                byte[] code = PrinterCommand.getCodeBarCommand(str, 70, 3, 168, 1, 2);
                                SendDataString("ITF\n");
                                SendDataByte(new byte[]{0x1b, 0x61, 0x00});
                                SendDataByte(code);
                            }
                        } else if (which == 6) {
                            if (str.length() == 0) {
                                Toast.makeText(Main_Activity.this, getText(R.string.msg_error), Toast.LENGTH_SHORT).show();
                                return;
                            } else {
                                byte[] code = PrinterCommand.getCodeBarCommand(str, 71, 3, 168, 1, 2);
                                SendDataString("CODABAR\n");
                                SendDataByte(new byte[]{0x1b, 0x61, 0x00});
                                SendDataByte(code);
                            }
                        } else if (which == 7) {
                            if (str.length() == 0) {
                                Toast.makeText(Main_Activity.this, getText(R.string.msg_error), Toast.LENGTH_SHORT).show();
                                return;
                            } else {
                                byte[] code = PrinterCommand.getCodeBarCommand(str, 72, 3, 168, 1, 2);
                                SendDataString("CODE93\n");
                                SendDataByte(new byte[]{0x1b, 0x61, 0x00});
                                SendDataByte(code);
                            }
                        } else if (which == 8) {
                            if (str.length() == 0) {
                                Toast.makeText(Main_Activity.this, getText(R.string.msg_error), Toast.LENGTH_SHORT).show();
                                return;
                            } else {
                                byte[] code = PrinterCommand.getCodeBarCommand(str, 73, 3, 168, 1, 2);
                                SendDataString("CODE128\n");
                                SendDataByte(new byte[]{0x1b, 0x61, 0x00});
                                SendDataByte(code);
                            }
                        } else if (which == 9) {
                            if (str.length() == 0) {
                                Toast.makeText(Main_Activity.this, getText(R.string.empty1), Toast.LENGTH_SHORT).show();
                                return;
                            } else {
                                byte[] code = PrinterCommand.getBarCommand(str, 1, 1, 5);
                                SendDataString("QR Code\n");
                                SendDataByte(new byte[]{0x1b, 0x61, 0x00});
                                SendDataByte(code);
                            }
                        }
                    }
                }).create().show();
    }

    public static Bitmap loadBitmapFromView(View v) {
        v.setDrawingCacheEnabled(true);
        v.setDrawingCacheQuality(View.DRAWING_CACHE_QUALITY_HIGH);
        v.setDrawingCacheBackgroundColor(Color.WHITE);

        int w = v.getWidth();
        int h = v.getHeight();

        Bitmap bmp = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888);
        Canvas c = new Canvas(bmp);

        c.drawColor(Color.WHITE);


        v.layout(v.getLeft(), v.getTop(), v.getRight(), v.getBottom());
        v.draw(c);

        return bmp;
    }

    private void GraphicalPrint() {

        String txt_msg = editText.getText().toString();
        if (txt_msg.length() == 0) {
            Looper.prepare();
            Toast.makeText(Main_Activity.this, getText(R.string.empty1), Toast.LENGTH_SHORT).show();
            Looper.loop();
            return;
        } else {
            //Bitmap bm1 = getImageFromAssetsFile("demo.jpg");
            if (width_58mm.isChecked()) {

                Bitmap bmp = loadBitmapFromView(editText);
                int nMode = 0;
                int nPaperWidth = 384;

                if (bmp != null) {
                    byte[] data = PrintPicture.POS_PrintBMP(bmp, nPaperWidth, nMode);
                    SendDataByte(Command.ESC_Init);
                    SendDataByte(Command.LF);
                    SendDataByte(data);
                    SendDataByte(PrinterCommand.POS_Set_PrtAndFeedPaper(30));
                    SendDataByte(PrinterCommand.POS_Set_Cut(1));
                    SendDataByte(PrinterCommand.POS_Set_PrtInit());
                }
            } else if (width_80.isChecked()) {
                //Bitmap bmp = Other.createAppIconText(bmp, txt_msg, 25, false, 200);
                int nMode = 0;

                int nPaperWidth = 576;
                Bitmap bmp = loadBitmapFromView(editText);
                if (bmp != null) {
                    byte[] data = PrintPicture.POS_PrintBMP(bmp, nPaperWidth, nMode);
                    SendDataByte(Command.ESC_Init);
                    SendDataByte(Command.LF);
                    SendDataByte(data);
                    SendDataByte(PrinterCommand.POS_Set_PrtAndFeedPaper(30));
                    SendDataByte(PrinterCommand.POS_Set_Cut(1));
                    SendDataByte(PrinterCommand.POS_Set_PrtInit());
                }
            }
        }
    }

    /**
     * Print instruction testing
     */
    private void CommandTest() {
                new AlertDialog.Builder(Main_Activity.this).setTitle(getText(R.string.chosecommand))
                    .setItems(itemsen, new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int which) {
                            SendDataByte(byteCommands[which]);
                            try {
                                if (which == 16 || which == 17 || which == 18 || which == 19 || which == 22
                                        || which == 23 || which == 24 || which == 0 || which == 1 || which == 27) {
                                    return;
                                } else {
                                    SendDataByte("Thermal Receipt Printer ABCDEFGabcdefg123456,.;'/[{}]!\nThermal Receipt PrinterABCDEFGabcdefg123456,.;'/[{}]!\nThermal Receipt PrinterABCDEFGabcdefg123456,.;'/[{}]!\nThermal Receipt PrinterABCDEFGabcdefg123456,.;'/[{}]!\nThermal Receipt PrinterABCDEFGabcdefg123456,.;'/[{}]!\nThermal Receipt PrinterABCDEFGabcdefg123456,.;'/[{}]!\n".getBytes(code));
                                }

                            } catch (UnsupportedEncodingException e) {
                                // TODO Auto-generated catch block
                                e.printStackTrace();
                            }
                        }
                    }).create().show();

    }

    /************************************************************************************************/
    /*
     * Generate QR Map
     */
    private void createImage() {
        try {

            QRCodeWriter writer = new QRCodeWriter();

            String text = editText.getText().toString();


            if (text == null || "".equals(text) || text.length() < 1) {
                Toast.makeText(this, getText(R.string.empty), Toast.LENGTH_SHORT).show();
                return;
            }

            // Convert the input text into QR code
            BitMatrix martix = writer.encode(text, BarcodeFormat.QR_CODE,
                    QR_WIDTH, QR_HEIGHT);

            System.out.println("w:" + martix.getWidth() + "h:"
                    + martix.getHeight());

            Hashtable<EncodeHintType, String> hints = new Hashtable<EncodeHintType, String>();
            hints.put(EncodeHintType.CHARACTER_SET, "utf-8");
            BitMatrix bitMatrix = new QRCodeWriter().encode(text,
                    BarcodeFormat.QR_CODE, QR_WIDTH, QR_HEIGHT, hints);
            int[] pixels = new int[QR_WIDTH * QR_HEIGHT];
            for (int y = 0; y < QR_HEIGHT; y++) {
                for (int x = 0; x < QR_WIDTH; x++) {
                    if (bitMatrix.get(x, y)) {
                        pixels[y * QR_WIDTH + x] = 0xff000000;
                    } else {
                        pixels[y * QR_WIDTH + x] = 0xffffffff;
                    }

                }
            }

            Bitmap bitmap = Bitmap.createBitmap(QR_WIDTH, QR_HEIGHT,
                    Bitmap.Config.ARGB_8888);

            bitmap.setPixels(pixels, 0, QR_WIDTH, 0, 0, QR_WIDTH, QR_HEIGHT);

            byte[] data = PrintPicture.POS_PrintBMP(bitmap, 384, 0);
            SendDataByte(data);
            SendDataByte(PrinterCommand.POS_Set_PrtAndFeedPaper(30));
            SendDataByte(PrinterCommand.POS_Set_Cut(1));
            SendDataByte(PrinterCommand.POS_Set_PrtInit());
        } catch (WriterException e) {
            e.printStackTrace();
        }
    }

    //************************************************************************************************//
    /*
     * Call system camera
     */
    private void dispatchTakePictureIntent(int actionCode) {
        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        startActivityForResult(takePictureIntent, actionCode);
    }

    private void handleSmallCameraPhoto(Intent intent) {
        Bundle extras = intent.getExtras();
        Bitmap mImageBitmap = (Bitmap) extras.get("data");
        imageViewPicture.setImageBitmap(mImageBitmap);
    }
/****************************************************************************************************/
    /**
     * Load assets file resources
     */
    private Bitmap getImageFromAssetsFile(String fileName) {
        Bitmap image = null;
        AssetManager am = getResources().getAssets();
        try {
            InputStream is = am.open(fileName);
            image = BitmapFactory.decodeStream(is);
            is.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return image;

    }

}