using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

static class Globals {
    public static List<int> idProcesados = new List<int>();
    public static List<int> jProcesados = new List<int>();
}

public static class JsonHelper
{
    public static T[] FromJson<T>(string json)
    {
        Wrapper<T> wrapper = JsonUtility.FromJson<Wrapper<T>>(json);
        return wrapper.Items;
    }
    public static string ToJson<T>(T[] array)
    {
        Wrapper<T> wrapper = new Wrapper<T>();
        wrapper.Items = array;
        return JsonUtility.ToJson(wrapper);
    }

    public static string ToJson<T>(T[] array, bool prettyPrint)
    {
        Wrapper<T> wrapper = new Wrapper<T>();
        wrapper.Items = array;
        return JsonUtility.ToJson(wrapper, prettyPrint);
    }

    [System.Serializable]
    private class Wrapper<T>
    {
        public T[] Items;
    }
}

[System.Serializable]
class MyAgent
{
    public int x;
    public int y;
    public string tipo;
    public int carrying;
    public int id;
    public int pickedBox;
    public bool picked;
    public int counterRobot;
    // public int inStack;
    // public bool inRobot;
    override public string ToString()
    {
        return "X: " + x + ", Y: " + y;
        // return "X: " + x + ", Y: " + y + ",Tipo: " + tipo + ",inStack: " + inStack + ",inRobot: " + inRobot;
    }
}

public class NewBehaviourScript : MonoBehaviour
{
    string simulationURL = null;
    private float waitTime = 0.5f; 
    private float timer = 0.0f;

    public GameObject prefabAgente;
    public int NumObjetos;
    List<GameObject> listaObj; //agents

    public GameObject prefabCaja;
    public int NumCaja;
    List<GameObject> listaCaja; 

    // Start is called before the first frame update
    void Start()

    {
        listaObj = new List<GameObject>();
        for (int i = 0; i < NumObjetos; i++)
        {
            float x = 3f;
            float y = 0f;
            float z = 3f;
            listaObj.Add(Instantiate(prefabAgente, new Vector3(x, y, z), Quaternion.identity));
        }

        listaCaja = new List<GameObject>();
        for (int i = 0; i < NumCaja; i++)
        {
            float x = 2f;
            float y = 0f;
            float z = 2f;
            listaCaja.Add(Instantiate(prefabCaja, new Vector3(x, y, z), Quaternion.identity));
        }

        StartCoroutine(ConnectToMesa());
    }
    IEnumerator ConnectToMesa()
    {
        WWWForm form = new WWWForm();

        using (UnityWebRequest www = UnityWebRequest.Post("http://localhost:5000/games", form))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.Log(www.error);
            }
            else
            {
                simulationURL = www.GetResponseHeader("Location");
                Debug.Log("Connected to simulation through Web API");
                Debug.Log(simulationURL);
            }
        }
    }

    IEnumerator UpdatePositions()
    {
        using (UnityWebRequest www = UnityWebRequest.Get(simulationURL))
        {
            if (simulationURL != null)
            {
                // Request and wait for the desired page.
                yield return www.SendWebRequest();

                Debug.Log(www.downloadHandler.text);
                Debug.Log("Data has been processed");

                MyAgent[] agents = JsonHelper.FromJson<MyAgent>(www.downloadHandler.text);
                Debug.Log(agents[0].ToString());
                int j = 0;
                int i = 0;
                
                foreach(MyAgent agent in agents){
                    //Debug.Log(agent);
                    if (agent.tipo == "Robot")
                    {
                        if (agent.carrying == 0 && agent.pickedBox != -1){
                            Debug.Log(agent.counterRobot);
                            while (Globals.jProcesados.Contains(j) && j < NumCaja-1)
                            {
                                j++;
                            }
                            listaCaja[j].transform.position = new Vector3(agent.x, agent.counterRobot * 0.8f, agent.y);
                            Globals.idProcesados.Add(agent.pickedBox);
                            Globals.jProcesados.Add(j);
                            j++;
                        }  

                        listaObj[i].transform.position = new Vector3(agent.x, 0.3f, agent.y);
                        if (i < NumObjetos){
                            i++;
                        }
                    }
                    else if (agent.tipo == "BoxBlock" && !Globals.idProcesados.Contains(agent.id))
                    {
                        while (Globals.jProcesados.Contains(j) && j < NumCaja-1)
                        {
                            j++;
                        }
                        if (agent.picked) {
                            Debug.Log("levantada");
                            listaCaja[j].transform.position = new Vector3(agent.x, -4.0f, agent.y);
                        } 

                        else{

                            listaCaja[j].transform.position = new Vector3(agent.x, 1.0f, agent.y);
                        }

                        if (j < NumCaja-1){

                            j++;
                        }
                        
                    
                    }
                }
            }
        }
    }

    // Update is called once per frame
    void Update()
    {
       timer += Time.deltaTime;
        if (timer > waitTime)
        {
            StartCoroutine(UpdatePositions());
            timer = timer - waitTime;
        } 
    }
}
