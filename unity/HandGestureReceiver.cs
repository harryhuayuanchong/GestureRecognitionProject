// unity/HandGestureReceiver.cs

using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public class HandGestureReceiver : MonoBehaviour
{
    private UdpClient udpClient;
    private IPEndPoint endPoint;

    void Start()
    {
        udpClient = new UdpClient(9000);
        endPoint = new IPEndPoint(IPAddress.Any, 9000);
    }

    void Update()
    {
        if (udpClient.Available > 0)
        {
            byte[] data = udpClient.Receive(ref endPoint);
            string json = Encoding.UTF8.GetString(data);
            HandGestureData handGestureData = JsonUtility.FromJson<HandGestureData>(json);
            ProcessHandGestureData(handGestureData);
        }
    }

    private void ProcessHandGestureData(HandGestureData handGestureData)
    {
        // 在此處處理接收到的手勢數據
        Debug.Log("Received hand gesture data: " + handGestureData);
    }

    void OnApplicationQuit()
    {
        udpClient.Close();
    }
}

[Serializable]
public class HandGestureData
{
    public Landmark[] landmarks;
}

[Serializable]
public class Landmark
{
    public float x;
    public float y;
    public float z;
}
