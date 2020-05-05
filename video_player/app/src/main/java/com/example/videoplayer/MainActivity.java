package com.example.videoplayer;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Context;
import android.media.MediaPlayer;
import android.os.AsyncTask;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.VideoView;
import android.os.Bundle;
import android.widget.ImageButton;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.*;
import android.content.BroadcastReceiver;
import android.widget.Toast;
import android.content.Intent;
import android.content.IntentFilter;

import java.io.ByteArrayOutputStream;
import java.io.Console;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.UUID;

import java.io.IOException;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class MainActivity extends AppCompatActivity {

    public VideoView videoView;
    ImageButton playButton;
    ImageButton stopButton;
    MediaPlayer mp;
    int REQUEST_ENABLE_BLUETOOTH = 0;

    private String DISPLAY_MAC_ADDR = "00:18:EA:0A:00:01"; //Arduino
//    private String DISPLAY_MAC_ADDR = "00:1B:DC:0F:45:35"; //Home
    private String SENSORS_URL = "http://192.168.245.228:8000";
    private String ADAPTER_UUID = "00001101-0000-1000-8000-00805F9B34FB";

    private BluetoothSocket socket;
    private BluetoothDevice device;
    private InputStream inputStream;
    private OutputStream outputStream;


    @Override
    protected void onCreate(Bundle savedInstanceState) {

        BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (bluetoothAdapter == null) {
            Toast.makeText(this, "Bluetooth is not available!", Toast.LENGTH_SHORT).show();
            finish(); //automatic close app if Bluetooth service is not available!
        }
        if (!bluetoothAdapter.isEnabled()) {
            Intent enableIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableIntent, REQUEST_ENABLE_BLUETOOTH);
        }
        if (bluetoothAdapter.isDiscovering()) {
            bluetoothAdapter.cancelDiscovery();
        }

        IntentFilter foundFilter = new IntentFilter(BluetoothDevice.ACTION_FOUND);
        registerReceiver(foundReceiver, foundFilter);

        bluetoothAdapter.startDiscovery();

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        videoView = findViewById(R.id.videoViewId);
        videoView.setVideoPath("android.resource://"+getPackageName()+"/"+R.raw.video);
        playButton = findViewById(R.id.playButton);
        stopButton = findViewById(R.id.stopButton);
        videoView.start();
        playButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                //videoView.seekTo(stopPosition);
//                videoView.start();
                // Code here executes on main thread after user presses button
                startVideo();
            }
        });
        stopButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                pauseVideo();
                // Code here executes on main thread after user presses button
            }
        });
    }

    MainActivity instance = this;

    private BroadcastReceiver foundReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {

            BluetoothDevice device1 = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);

            String msg = device1.getAddress() + " | " + device1.getName();
            Log.d("BLUETOOTH", msg);
            Toast.makeText(instance, msg, Toast.LENGTH_SHORT).show();

            if (!device1.getAddress().equals(DISPLAY_MAC_ADDR))
                return;

            Toast.makeText(instance, msg + " | Connected", Toast.LENGTH_SHORT).show();

            device = device1;
        }
    };

    OkHttpClient client = new OkHttpClient();

    void doGetRequest(String url) throws IOException{
        Request request = new Request.Builder()
                .url(url)
                .build();

        client.newCall(request)
                .enqueue(new Callback() {
                    @Override
                    public void onFailure(final Call call, final IOException e) {
                        // Error

                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                // For the example, you can show an error dialog or a toast
                                // on the main UI thread
                                Log.e("RESPONSE_NEUROGRAPH", "", e);
                            }
                        });
                    }

                    @Override
                    public void onResponse(Call call, final Response response) throws IOException {
                        String res = response.body().string();
                        Log.d("RESPONSE_NEUROGRAPH", res);
                        sendBluetooth(res.getBytes());
                        // Do something with the response
                    }
                });
    }

    public void sendBluetooth(int b) {
        sendBluetooth(new byte[]{(byte) b});
    }

    public void sendBluetooth(byte[] data) {
        try {
            socket = device.createInsecureRfcommSocketToServiceRecord(UUID.fromString(ADAPTER_UUID));

            socket.connect();
            Log.d("EF-BTBee", ">>Client connectted");

            inputStream = socket.getInputStream();
            outputStream = socket.getOutputStream();

            outputStream.write(data);

        } catch (Exception e) {
            Log.e("EF-BTBee", "", e);
        } finally {
            if (socket != null) {
                try {
                    Log.d("EF-BTBee", ">>Client Close");
                    socket.close();
                } catch (IOException e) {
                    Log.e("EF-BTBee", "", e);
                }
            }
        }
    }

    public void startVideo()
    {
        videoView.start();
        try {
            doGetRequest(SENSORS_URL);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    public void pauseVideo()
    {
        sendBluetooth(0xa0);
        videoView.pause();
    }
}