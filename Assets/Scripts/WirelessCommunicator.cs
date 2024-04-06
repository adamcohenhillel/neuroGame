using System;
using System.Collections;
using System.Collections.Generic;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public class WirelessCommunicator : MonoBehaviour
{
    private TcpClient client;
    private NetworkStream stream;
    private byte[] dataBuffer = new byte[1024];
    private string serverIP = "127.0.0.1"; // Example server IP, change as needed
    private int serverPort = 8080; // Example server port, change as needed

    void Start()
    {
        try
        {
            client = new TcpClient(serverIP, serverPort);
            stream = client.GetStream();
            Debug.Log("Connected to server");
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to connect to server: {e.Message}");
        }
    }

    void Update()
    {
        if (client != null && client.Connected && stream.DataAvailable)
        {
            int bytesRead = stream.Read(dataBuffer, 0, dataBuffer.Length);
            string message = Encoding.UTF8.GetString(dataBuffer, 0, bytesRead);
            Debug.Log($"Received: {message}");
        }
    }

    void OnDestroy()
    {
        if (stream != null)
        {
            stream.Close();
        }

        if (client != null)
        {
            client.Close();
        }
    }
}
